import httpx

from app.config import settings

PLACES_SEARCH_TEXT_URL = "https://places.googleapis.com/v1/places:searchText"
FIELD_MASK = ",".join(
    [
        "places.id",
        "places.displayName",
        "places.formattedAddress",
        "places.internationalPhoneNumber",
        "places.googleMapsUri",
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
        while len(leads) < quantidade_alvo:
            resp = await client.post(PLACES_SEARCH_TEXT_URL, headers=headers, json=body)
            resp.raise_for_status()
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
                    }
                )

            next_page_token = data.get("nextPageToken")
            if not next_page_token or len(leads) >= quantidade_alvo:
                break
            body = {"textQuery": body["textQuery"], "pageToken": next_page_token}

    return leads
