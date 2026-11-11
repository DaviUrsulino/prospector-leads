"""
Disparo automático diário: 20 leads saúde + 20 leads outras áreas.
Horário de início sorteia entre 8:30 e 10:30 (varia todo dia).
Delay entre contatos: 5-15 min aleatório.
Dentro de cada contato: 5 msgs com 6-9s entre elas (simula digitação).
"""
import asyncio
import logging
import random
from datetime import datetime, timezone

from app.database import SessionLocal
from app.models import Busca, LeadEncontrado
from app.services import whatsapp
from app.services.dedup import filtrar_leads_novos, remover_duplicatas_do_lote
from app.services.enrichment import enriquecer_leads
from app.services.places import buscar_leads

logger = logging.getLogger(__name__)

TERMOS_SAUDE = [
    "médico", "dentista", "psicólogo", "fisioterapeuta", "nutricionista",
    "oftalmologista", "dermatologista", "cardiologista", "ortopedista",
    "pediatra", "ginecologista", "neurologista", "endocrinologista",
    "urologista", "otorrinolaringologista", "clínica médica",
]

TERMOS_OUTROS = [
    "advogado", "contador", "arquiteto", "engenheiro civil", "corretor de imóveis",
    "personal trainer", "fotógrafo", "designer gráfico", "consultor de negócios",
    "coach", "veterinário", "academia", "escola de idiomas", "estúdio de pilates",
    "clínica de estética", "barbearia", "salão de beleza",
]

# Entre contatos: 5-15 min aleatório
DELAY_MIN_S = 300
DELAY_MAX_S = 900


async def _buscar_e_salvar(termo: str, quantidade: int, db) -> list[LeadEncontrado]:
    cidade = "Brasília"
    leads_raw = await buscar_leads(cidade, termo, quantidade)
    leads_raw = remover_duplicatas_do_lote(leads_raw)
    leads_raw = filtrar_leads_novos(db, leads_raw)
    leads_raw = leads_raw[:quantidade]
    if not leads_raw:
        return []
    leads_raw = await enriquecer_leads(leads_raw)
    busca = Busca(cidade=cidade, termo=termo, quantidade_alvo=quantidade)
    busca.leads = [LeadEncontrado(**lead, ordem=i) for i, lead in enumerate(leads_raw)]
    db.add(busca)
    db.commit()
    db.refresh(busca)
    return list(busca.leads)


async def executar_disparo_diario() -> None:
    # Horário de início aleatório entre 8:30 e 10:30 — sorteia delay inicial
    agora = datetime.now(timezone.utc).astimezone()
    hora_atual = agora.hour + agora.minute / 60

    # Janela permitida: 8:30 até 18:00
    if hora_atual < 8.5:
        # Espera até 8:30 + offset aleatório de até 2h
        segundos_ate_830 = (8.5 - hora_atual) * 3600
        offset_aleatorio = random.uniform(0, 7200)  # até 2h extras
        await asyncio.sleep(segundos_ate_830 + offset_aleatorio)
    elif hora_atual >= 18.0:
        logger.info("Disparo automático fora do horário (já passou das 18h), pulando.")
        return

    logger.info("Iniciando disparo automático diário")
    db = SessionLocal()
    try:
        termo_saude = random.choice(TERMOS_SAUDE)
        termo_outro = random.choice(TERMOS_OUTROS)
        leads_saude = await _buscar_e_salvar(termo_saude, 20, db)
        leads_outros = await _buscar_e_salvar(termo_outro, 20, db)
        # Extrai dados em dicts antes de fechar a session
        leads = [
            {"id": l.id, "nome": l.nome, "numero": l.whatsapp_direto or l.telefone}
            for l in (leads_saude + leads_outros)
        ]
        random.shuffle(leads)
        n_saude = len(leads_saude)
        n_outros = len(leads_outros)
    finally:
        db.close()

    logger.info(
        f"Disparo automático: {len(leads)} leads "
        f"({n_saude} saúde [{termo_saude}] + {n_outros} outros [{termo_outro}])"
    )

    for i, lead in enumerate(leads):
        agora = datetime.now(timezone.utc).astimezone()
        if agora.hour >= 18:
            logger.info("Horário limite atingido (18:00), encerrando disparo.")
            break

        lead_id = lead["id"]
        numero = lead["numero"]
        nome = lead["nome"]

        if not numero:
            continue

        db = SessionLocal()
        try:
            lead_db = db.query(LeadEncontrado).filter(LeadEncontrado.id == lead_id).first()
            if not lead_db or lead_db.mensagem_enviada_em:
                continue
            await whatsapp.enviar_mensagens(numero, nome)
            lead_db.mensagem_enviada_em = datetime.now(timezone.utc)
            db.commit()
            logger.info(f"[{i+1}/{len(leads)}] Enviado: {nome}")
        except Exception as exc:
            logger.error(f"Erro lead {lead_id} ({nome}): {exc}")
        finally:
            db.close()

        if i < len(leads) - 1:
            delay = random.uniform(DELAY_MIN_S, DELAY_MAX_S)
            logger.info(f"Próximo contato em {delay/60:.1f} min")
            await asyncio.sleep(delay)

    logger.info("Disparo automático diário concluído.")
