import asyncio
import re

import httpx

from app.config import settings

# Vários sites de negócio pequeno (WordPress, principalmente) usam plugin de
# firewall (mod_security e afins) que barra qualquer User-Agent de "bot"
# antes mesmo de mandar o HTML. Um cabeçalho de navegador normal evita esse
# bloqueio — continuamos batendo só na página pública do próprio lead.
HEADERS_NAVEGADOR = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.8",
}

_REDES = {
    "instagram": re.compile(
        r'href=["\'](?:https?:)?//?(?:www\.)?instagram\.com/(?!p/|reel/|explore/)[^"\'?#/]+',
        re.IGNORECASE,
    ),
    "linkedin": re.compile(
        r'href=["\'](?:https?:)?//?(?:www\.)?linkedin\.com/(?:company|in)/[^"\'?#]+',
        re.IGNORECASE,
    ),
    "facebook": re.compile(
        r'href=["\'](?:https?:)?//?(?:www\.)?facebook\.com/(?!sharer|share)[^"\'?#/]+',
        re.IGNORECASE,
    ),
}

_EMAIL = re.compile(r'href=["\']mailto:([^"\'?]+)', re.IGNORECASE)
_WHATSAPP = re.compile(
    r'href=["\'](?:https?:)?//?(?:api\.)?(?:whatsapp\.com/send\?phone=|wa\.me/)(\d+)',
    re.IGNORECASE,
)


def _extrair_url(match: re.Match) -> str:
    url = match.group(0).split("=", 1)[1].strip("\"'")
    if url.startswith("//"):
        return f"https:{url}"
    if not url.startswith("http"):
        return f"https://{url}"
    return url


async def enriquecer_redes_sociais(website: str | None) -> dict:
    vazio = {
        "instagram": None,
        "linkedin": None,
        "facebook": None,
        "email": None,
        "whatsapp_direto": None,
    }
    if not website:
        return vazio

    try:
        async with httpx.AsyncClient(
            timeout=settings.enrichment_timeout_seconds,
            follow_redirects=True,
            headers=HEADERS_NAVEGADOR,
        ) as client:
            resp = await client.get(website)
            resp.raise_for_status()
            html = resp.text
    except (httpx.HTTPError, httpx.InvalidURL):
        return vazio

    resultado = dict(vazio)
    for rede, padrao in _REDES.items():
        match = padrao.search(html)
        if match:
            resultado[rede] = _extrair_url(match)

    match_email = _EMAIL.search(html)
    if match_email:
        resultado["email"] = match_email.group(1).strip()

    match_whatsapp = _WHATSAPP.search(html)
    if match_whatsapp:
        resultado["whatsapp_direto"] = match_whatsapp.group(1)

    return resultado


async def enriquecer_leads(leads: list[dict]) -> list[dict]:
    semaforo = asyncio.Semaphore(settings.enrichment_concurrency)

    async def _enriquecer_um(lead: dict) -> dict:
        async with semaforo:
            redes = await enriquecer_redes_sociais(lead.get("website"))
        return {**lead, **redes}

    return list(await asyncio.gather(*(_enriquecer_um(lead) for lead in leads)))


_CAMPOS_CONTATO = (
    "telefone",
    "website",
    "instagram",
    "linkedin",
    "facebook",
    "email",
    "whatsapp_direto",
)


def _completude(lead: dict) -> int:
    return sum(1 for campo in _CAMPOS_CONTATO if lead.get(campo))


def ordenar_por_completude(leads: list[dict]) -> list[dict]:
    """Lead com mais dado de contato preenchido aparece primeiro."""
    return sorted(leads, key=_completude, reverse=True)
