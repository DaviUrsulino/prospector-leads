import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.services.places import buscar_leads

router = APIRouter(prefix="/buscas", tags=["buscas"])
limiter = Limiter(key_func=get_remote_address)


@router.post("", response_model=schemas.BuscaComLeadsOut)
@limiter.limit("10/minute")
async def criar_busca(
    request: Request,
    payload: schemas.BuscaCreate,
    db: Session = Depends(get_db),
):
    leads_encontrados = await buscar_leads(
        payload.cidade, payload.termo.value, payload.quantidade_alvo
    )

    busca = models.Busca(
        cidade=payload.cidade,
        termo=payload.termo.value,
        quantidade_alvo=payload.quantidade_alvo,
    )
    busca.leads = [models.LeadEncontrado(**lead) for lead in leads_encontrados]

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


@router.patch("/{busca_id}/leads/{lead_id}/favorito", response_model=schemas.LeadEncontradoOut)
def alternar_favorito(busca_id: str, lead_id: str, db: Session = Depends(get_db)):
    lead = (
        db.query(models.LeadEncontrado)
        .filter(models.LeadEncontrado.id == lead_id, models.LeadEncontrado.busca_id == busca_id)
        .first()
    )
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    lead.favorito = not lead.favorito
    db.commit()
    db.refresh(lead)
    return lead


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
        ["nome", "telefone", "endereco", "especialidade", "link_perfil", "favorito"]
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
            ]
        )
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=busca-{busca_id}.csv"},
    )
