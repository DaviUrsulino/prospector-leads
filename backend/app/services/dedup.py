from sqlalchemy import or_
from sqlalchemy.orm import Session

from app import models


def remover_duplicatas_do_lote(leads: list[dict]) -> list[dict]:
    """Remove repetição dentro da mesma leva (ex: duas especialidades da
    mesma busca acharam o mesmo estabelecimento)."""
    vistos_place_id: set[str] = set()
    vistos_telefone: set[str] = set()
    resultado: list[dict] = []

    for lead in leads:
        place_id = lead.get("place_id")
        telefone = lead.get("telefone")
        if place_id and place_id in vistos_place_id:
            continue
        if telefone and telefone in vistos_telefone:
            continue
        if place_id:
            vistos_place_id.add(place_id)
        if telefone:
            vistos_telefone.add(telefone)
        resultado.append(lead)

    return resultado


def filtrar_leads_novos(db: Session, leads: list[dict]) -> list[dict]:
    """Descarta lead que já apareceu em qualquer busca anterior (mesmo
    place_id ou telefone), pra não repetir contato já prospectado."""
    place_ids = {lead["place_id"] for lead in leads if lead.get("place_id")}
    telefones = {lead["telefone"] for lead in leads if lead.get("telefone")}

    if not place_ids and not telefones:
        return leads

    condicoes = []
    if place_ids:
        condicoes.append(models.LeadEncontrado.place_id.in_(place_ids))
    if telefones:
        condicoes.append(models.LeadEncontrado.telefone.in_(telefones))

    existentes = (
        db.query(models.LeadEncontrado.place_id, models.LeadEncontrado.telefone)
        .filter(or_(*condicoes))
        .all()
    )
    place_ids_vistos = {p for p, _ in existentes if p}
    telefones_vistos = {t for _, t in existentes if t}

    return [
        lead
        for lead in leads
        if lead.get("place_id") not in place_ids_vistos
        and lead.get("telefone") not in telefones_vistos
    ]
