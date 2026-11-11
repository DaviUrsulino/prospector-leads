import asyncio
import csv
import io
import math
from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import SessionLocal, get_db
from app.services import whatsapp
from app.services.auto_disparo import executar_disparo_diario
from app.services.dedup import filtrar_leads_novos, remover_duplicatas_do_lote
from app.services.enrichment import enriquecer_leads, ordenar_por_completude
from app.services.osm_fallback import buscar_leads_osm
from app.services.places import PAGE_SIZE, buscar_leads
from app.services.regioes import descarta_fora_do_df, regioes_extras

router = APIRouter(prefix="/buscas", tags=["buscas"])
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=schemas.BuscaComLeadsOut)
@limiter.limit("10/minute")
async def criar_busca(
    request: Request,
    payload: schemas.BuscaCreate,
    db: Session = Depends(get_db),
):
    # Busca desde o início em Brasília + regiões metropolitanas (Ceilândia,
    # Taguatinga, Águas Claras etc.), não só quando falta — senão, com um
    # alvo baixo (ex: 20), uma página só do Plano Piloto já "bate a meta" e
    # o resto da região nunca chega a ser tentado.
    # Pede até uma página cheia (20) de cada área — a Places cobra por
    # chamada, não por quantidade de resultado dentro da mesma chamada, então
    # pedir pouco de cada área só faz o sistema parar cedo demais sem custar
    # menos (foi exatamente esse o bug: dividir o alvo entre 9 áreas pedia
    # só 2-3 de cada uma, e a busca "batia a meta" bem antes de esgotar
    # qualquer área de verdade).
    areas = [payload.cidade] + regioes_extras(payload.cidade)
    por_termo = math.ceil(payload.quantidade_alvo / len(payload.termos))
    por_area = min(por_termo, PAGE_SIZE)

    leads_encontrados: list[dict] = []
    for termo in payload.termos:
        for area in areas:
            leads_encontrados += await buscar_leads(area, termo, por_area)
    leads_encontrados = remover_duplicatas_do_lote(leads_encontrados)

    faltam = payload.quantidade_alvo - len(leads_encontrados)
    if faltam > 0:
        termo_combinado = " / ".join(payload.termos)
        leads_encontrados += await buscar_leads_osm(payload.cidade, termo_combinado, faltam)
        leads_encontrados = remover_duplicatas_do_lote(leads_encontrados)
        faltam = payload.quantidade_alvo - len(leads_encontrados)

    # Reforço: se as áreas deram pouco (especialidade rara), pede mais de
    # cada uma até completar ou esgotar as opções.
    if faltam > 0:
        for area in areas:
            if faltam <= 0:
                break
            for termo in payload.termos:
                if faltam <= 0:
                    break
                leads_encontrados += await buscar_leads(area, termo, faltam)
                leads_encontrados = remover_duplicatas_do_lote(leads_encontrados)
                faltam = payload.quantidade_alvo - len(leads_encontrados)

    leads_encontrados = descarta_fora_do_df(leads_encontrados, payload.cidade)
    leads_encontrados = filtrar_leads_novos(db, leads_encontrados)
    leads_encontrados = leads_encontrados[: payload.quantidade_alvo]

    leads_encontrados = await enriquecer_leads(leads_encontrados)
    leads_encontrados = ordenar_por_completude(leads_encontrados)

    busca = models.Busca(
        cidade=payload.cidade,
        termo=", ".join(payload.termos),
        quantidade_alvo=payload.quantidade_alvo,
    )
    busca.leads = [
        models.LeadEncontrado(**lead, ordem=i) for i, lead in enumerate(leads_encontrados)
    ]

    db.add(busca)
    db.commit()
    db.refresh(busca)
    return busca


@router.get("", response_model=list[schemas.BuscaOut])
def listar_buscas(db: Session = Depends(get_db)):
    return db.query(models.Busca).order_by(models.Busca.criada_em.desc()).all()


@router.get("/estatisticas", response_model=schemas.EstatisticasOut)
def obter_estatisticas(db: Session = Depends(get_db)):
    total_buscas = db.query(func.count(models.Busca.id)).scalar() or 0
    total_leads = db.query(func.count(models.LeadEncontrado.id)).scalar() or 0
    leads_com_telefone = (
        db.query(func.count(models.LeadEncontrado.id))
        .filter(models.LeadEncontrado.telefone.isnot(None))
        .scalar()
        or 0
    )
    pct_com_telefone = (leads_com_telefone / total_leads * 100) if total_leads else 0.0
    total_favoritos = (
        db.query(func.count(models.LeadEncontrado.id))
        .filter(models.LeadEncontrado.favorito.is_(True))
        .scalar()
        or 0
    )

    ultimas_buscas = (
        db.query(models.Busca).order_by(models.Busca.criada_em.desc()).limit(5).all()
    )

    return schemas.EstatisticasOut(
        total_buscas=total_buscas,
        total_leads=total_leads,
        pct_leads_com_telefone=round(pct_com_telefone, 1),
        total_favoritos=total_favoritos,
        ultimas_buscas=ultimas_buscas,
    )


@router.get("/{busca_id}", response_model=schemas.BuscaComLeadsOut)
def obter_busca(busca_id: str, db: Session = Depends(get_db)):
    busca = db.query(models.Busca).filter(models.Busca.id == busca_id).first()
    if not busca:
        raise HTTPException(status_code=404, detail="Busca não encontrada")
    return busca


@router.patch("/{busca_id}/leads/{lead_id}/contatado", response_model=schemas.LeadEncontradoOut)
def set_contatado(busca_id: str, lead_id: str, valor: bool, db: Session = Depends(get_db)):
    lead = (
        db.query(models.LeadEncontrado)
        .filter(models.LeadEncontrado.id == lead_id, models.LeadEncontrado.busca_id == busca_id)
        .first()
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead.contatado = valor
    db.commit()
    db.refresh(lead)
    return lead


@router.patch("/{busca_id}/leads/{lead_id}/favorito", response_model=schemas.LeadEncontradoOut)
def set_favorito(busca_id: str, lead_id: str, valor: bool, db: Session = Depends(get_db)):
    lead = (
        db.query(models.LeadEncontrado)
        .filter(models.LeadEncontrado.id == lead_id, models.LeadEncontrado.busca_id == busca_id)
        .first()
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead.favorito = valor
    db.commit()
    db.refresh(lead)
    return lead


class _DisparoStatus(BaseModel):
    total: int
    sem_numero: int
    ja_enviados: int
    disparando: int


@router.post("/{busca_id}/leads/{lead_id}/disparar", response_model=schemas.LeadEncontradoOut)
async def disparar_lead(busca_id: str, lead_id: str, db: Session = Depends(get_db)):
    lead = (
        db.query(models.LeadEncontrado)
        .filter(models.LeadEncontrado.id == lead_id, models.LeadEncontrado.busca_id == busca_id)
        .first()
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    numero = lead.whatsapp_direto or lead.telefone
    if not numero:
        raise HTTPException(status_code=400, detail="Lead sem número de contato")

    await whatsapp.enviar_mensagens(numero, lead.nome)
    lead.mensagem_enviada_em = datetime.now(timezone.utc)
    db.commit()
    db.refresh(lead)
    return lead


async def _disparar_em_lote(lead_ids: list[str]) -> None:
    for i, lead_id in enumerate(lead_ids):
        db = SessionLocal()
        try:
            lead = db.query(models.LeadEncontrado).filter(models.LeadEncontrado.id == lead_id).first()
            if not lead or lead.mensagem_enviada_em:
                continue
            numero = lead.whatsapp_direto or lead.telefone
            if not numero:
                continue
            await whatsapp.enviar_mensagens(numero, lead.nome)
            lead.mensagem_enviada_em = datetime.now(timezone.utc)
            db.commit()
        except Exception:
            pass
        finally:
            db.close()
        if i < len(lead_ids) - 1:
            await asyncio.sleep(8)


@router.post("/{busca_id}/disparar")
async def disparar_busca(
    busca_id: str, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
):
    busca = db.query(models.Busca).filter(models.Busca.id == busca_id).first()
    if not busca:
        raise HTTPException(status_code=404, detail="Busca não encontrada")

    sem_numero = sum(1 for l in busca.leads if not l.whatsapp_direto and not l.telefone)
    ja_enviados = sum(1 for l in busca.leads if l.mensagem_enviada_em is not None)
    pendentes = [
        l.id
        for l in busca.leads
        if l.mensagem_enviada_em is None and (l.whatsapp_direto or l.telefone)
    ]

    background_tasks.add_task(_disparar_em_lote, pendentes)

    return _DisparoStatus(
        total=len(busca.leads),
        sem_numero=sem_numero,
        ja_enviados=ja_enviados,
        disparando=len(pendentes),
    )


@router.post("/disparar-agora", status_code=202)
async def disparar_agora(background_tasks: BackgroundTasks):
    """Dispara o ciclo automático imediatamente (sem esperar o agendamento diário)."""
    background_tasks.add_task(executar_disparo_diario)
    return {"status": "iniciado"}


@router.delete("/{busca_id}", status_code=204)
def excluir_busca(busca_id: str, db: Session = Depends(get_db)):
    busca = db.query(models.Busca).filter(models.Busca.id == busca_id).first()
    if not busca:
        raise HTTPException(status_code=404, detail="Busca não encontrada")
    db.delete(busca)
    db.commit()


@router.get("/{busca_id}/export")
def exportar_busca_csv(busca_id: str, db: Session = Depends(get_db)):
    busca = db.query(models.Busca).filter(models.Busca.id == busca_id).first()
    if not busca:
        raise HTTPException(status_code=404, detail="Busca não encontrada")

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "nome",
            "telefone",
            "endereco",
            "especialidade",
            "link_perfil",
            "favorito",
            "contatado",
            "website",
            "instagram",
            "linkedin",
            "facebook",
            "email",
            "whatsapp_direto",
            "fonte",
        ]
    )
    for lead in busca.leads:
        writer.writerow(
            [
                lead.nome,
                lead.telefone,
                lead.endereco,
                lead.especialidade,
                lead.link_perfil,
                lead.favorito,
                lead.contatado,
                lead.website,
                lead.instagram,
                lead.linkedin,
                lead.facebook,
                lead.email,
                lead.whatsapp_direto,
                lead.fonte,
            ]
        )
    # BOM UTF-8 na frente: sem isso o Excel (principalmente em PT-BR) abre
    # com encoding errado e os acentos saem trocados.
    conteudo = "﻿" + buffer.getvalue()

    return StreamingResponse(
        iter([conteudo.encode("utf-8")]),
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename=busca-{busca_id}.csv"},
    )
