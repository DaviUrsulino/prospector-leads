import asyncio

import httpx

from app.config import settings

PLACES_SEARCH_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"
# A Places API (New) demora um pouco pra ativar o nextPageToken; usar antes
# disso devolve erro e derruba a página seguinte à toa (já paga).
DELAY_PROXIMA_PAGINA_SEGUNDOS = 2
FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.internationalPhoneNumber",
        "places.googleMapsUri",
        "places.websiteUri",
    ]
)
PAGE_SIZE = 20  # máximo aceito pelo Text Search (New) por página


def _mock_leads(cidade: str, termo: str, quantidade_alvo: int) -> list[dict]:
    """Dados falsos, usados enquanto não há GOOGLE_PLACES_API_KEY configurada."""
    return [
        {
            "nome": f"{termo.capitalize()} Exemplo {i + 1} - {cidade}",
            "telefone": f"+55 61 9{9000 + i:04d}-{1000 + i:04d}",
            "endereco": f"Rua Fictícia, {100 + i} - {cidade}",
            "especialidade": termo,
            "place_id": f"mock-{cidade}-{termo}-{i}",
            "link_perfil": None,
            "website": None,
            "fonte": "google_places",
        }
        for i in range(min(quantidade_alvo, 20))
    ]


async def buscar_leads(cidade: str, termo: str, quantidade_alvo: int) -> list[dict]:
    if not settings.google_places_api_key:
        return _mock_leads(cidade, termo, quantidade_alvo)

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": settings.google_places_api_key,
        "X-Goog-FieldMask": FIELD_MASK,
    }
    body: dict = {
        "textQuery": f"{termo} em {cidade}",
        "pageSize": min(PAGE_SIZE, quantidade_alvo),
        "languageCode": "pt-BR",
    }

    leads: list[dict] = []

    async with httpx.AsyncClient(timeout=10) as client:
        primeira_pagina = True
        while len(leads) < quantidade_alvo:
            if not primeira_pagina:
                await asyncio.sleep(DELAY_PROXIMA_PAGINA_SEGUNDOS)
            primeira_pagina = False

            resp = await client.post(PLACES_SEARCH_TEXT_URL, headers=headers, json=body)
            if not leads:
                # primeira página: erro aqui é real, não tem leads pra preservar
                resp.raise_for_status()
            elif resp.status_code >= 400:
                # já temos leads pagos da(s) página(s) anterior(es); não jogar fora
                break
            data = resp.json()

            for place in data.get("places", []):
                if len(leads) >= quantidade_alvo:
                    break
                leads.append(
                    {
                        "nome": place.get("displayName", {}).get("text", ""),
                        "telefone": place.get("internationalPhoneNumber"),
                        "endereco": place.get("formattedAddress"),
                        "especialidade": termo,
                        "place_id": place.get("id"),
                        "link_perfil": place.get("googleMapsUri"),
                        "website": place.get("websiteUri"),
                        "fonte": "google_places",
                    }
                )

            next_page_token = data.get("nextPageToken")
            if not next_page_token or len(leads) >= quantidade_alvo:
                break
            body = {"textQuery": body["textQuery"], "pageToken": next_page_token}

    return leads
