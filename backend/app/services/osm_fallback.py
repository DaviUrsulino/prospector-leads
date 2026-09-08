import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "ProspectorLeadsBot/1.0 (uso educacional, fallback gratuito via OpenStreetMap)"
TIMEOUT = 10


async def _geocodificar_cidade(client: httpx.AsyncClient, cidade: str) -> tuple[float, float, float, float] | None:
    resp = await client.get(
        NOMINATIM_URL,
        params={"q": cidade, "format": "json", "limit": 1},
        headers={"User-Agent": USER_AGENT},
    )
    resp.raise_for_status()
    resultados = resp.json()
    if not resultados:
        return None

    sul, norte, oeste, leste = (float(v) for v in resultados[0]["boundingbox"])
    return sul, oeste, norte, leste


def _montar_query_overpass(termo: str, bbox: tuple[float, float, float, float]) -> str:
    sul, oeste, norte, leste = bbox
    caixa = f"{sul},{oeste},{norte},{leste}"
    return f"""
    [out:json][timeout:15];
    (
      node["name"~"{termo}",i]({caixa});
      way["name"~"{termo}",i]({caixa});
    );
    out center 60;
    """


def _montar_endereco(tags: dict) -> str | None:
    partes = [
        tags.get("addr:street"),
        tags.get("addr:housenumber"),
        tags.get("addr:suburb"),
        tags.get("addr:city"),
    ]
    partes = [p for p in partes if p]
    return ", ".join(partes) if partes else None


async def buscar_leads_osm(cidade: str, termo: str, quantidade: int) -> list[dict]:
    if quantidade <= 0:
        return []

    try:
        async with httpx.AsyncClient(timeout=TIMEOUT, headers={"User-Agent": USER_AGENT}) as client:
            bbox = await _geocodificar_cidade(client, cidade)
            if bbox is None:
                return []

            resp = await client.post(
                OVERPASS_URL, data={"data": _montar_query_overpass(termo, bbox)}
            )
            resp.raise_for_status()
            elementos = resp.json().get("elements", [])
    except (httpx.HTTPError, ValueError, KeyError):
        return []

    leads: list[dict] = []
    for el in elementos:
        if len(leads) >= quantidade:
            break
        tags = el.get("tags", {})
        nome = tags.get("name")
        if not nome:
            continue
        leads.append(
            {
                "nome": nome,
                "telefone": tags.get("phone") or tags.get("contact:phone"),
                "endereco": _montar_endereco(tags),
                "especialidade": termo,
                "place_id": f"osm-{el.get('type')}-{el.get('id')}",
                "link_perfil": tags.get("website"),
                "website": tags.get("website"),
                "fonte": "osm",
            }
        )

    return leads
