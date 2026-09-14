from sqlalchemy.orm import Session

from app import models


def _normalizar_telefone(telefone: str | None) -> str | None:
    """Só os dígitos — sem isso, '+55 61 3245-6789' (Google) e
    '5561999998888' (OSM/WhatsApp) são tratados como números diferentes
    mesmo sendo o mesmo, e o mesmo negócio aparece duas vezes na lista."""
    if not telefone:
        return None
    digitos = "".join(c for c in telefone if c.isdigit())
    return digitos or None


def remover_duplicatas_do_lote(leads: list[dict]) -> list[dict]:
    """Remove repetição dentro da mesma leva (ex: duas especialidades da
    mesma busca acharam o mesmo estabelecimento, ou o mesmo negócio veio
    tanto da Places quanto do fallback OSM)."""
    vistos_place_id: set[str] = set()
    vistos_telefone: set[str] = set()
    resultado: list[dict] = []

    for lead in leads:
        place_id = lead.get("place_id")
        telefone = _normalizar_telefone(lead.get("telefone"))
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
    place_id ou telefone, comparado só pelos dígitos), pra não repetir
    contato já prospectado."""
    place_ids = {lead["place_id"] for lead in leads if lead.get("place_id")}
    telefones = {_normalizar_telefone(lead.get("telefone")) for lead in leads}
    telefones.discard(None)

    if not place_ids and not telefones:
        return leads

    # O volume de leads hoje é pequeno o bastante pra trazer a tabela
    # inteira e comparar em Python — filtrar telefone por igualdade exata
    # no SQL não pegaria os números com formatação diferente.
    existentes = db.query(
        models.LeadEncontrado.place_id, models.LeadEncontrado.telefone
    ).all()
    place_ids_vistos = {p for p, _ in existentes if p}
    telefones_vistos = {_normalizar_telefone(t) for _, t in existentes}
    telefones_vistos.discard(None)

    return [
        lead
        for lead in leads
        if lead.get("place_id") not in place_ids_vistos
        and _normalizar_telefone(lead.get("telefone")) not in telefones_vistos
    ]
