import httpx

from app.config import settings

PLACES_TEXT_SEARCH_URL = "https://maps.googleapis.com/maps/api/place/textsearch/json"
PLACES_DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"


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

    query = f"{termo} em {cidade}"
    leads: list[dict] = []
    params = {"query": query, "key": settings.google_places_api_key}

    async with httpx.AsyncClient(timeout=10) as client:
        while len(leads) < quantidade_alvo:
            resp = await client.get(PLACES_TEXT_SEARCH_URL, params=params)
            resp.raise_for_status()
            data = resp.json()

            for place in data.get("results", []):
                if len(leads) >= quantidade_alvo:
                    break
                leads.append(
                    {
                        "nome": place.get("name", ""),
                        # Text Search não retorna telefone; precisaria de uma chamada
                        # extra ao endpoint Place Details por resultado (custo maior).
                        "telefone": None,
                        "endereco": place.get("formatted_address"),
                        "especialidade": termo,
                        "place_id": place.get("place_id"),
                        "link_perfil": None,
                    }
                )

            next_page_token = data.get("next_page_token")
            if not next_page_token or len(leads) >= quantidade_alvo:
                break
            params = {"pagetoken": next_page_token, "key": settings.google_places_api_key}

    return leads
