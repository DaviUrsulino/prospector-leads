import httpx

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
USER_AGENT = "ProspectorLeadsBot/1.0 (uso educacional, fallback gratuito via OpenStreetMap)"
TIMEOUT = 10


async def _geocodificar_cidade(client: httpx.AsyncClient, cidade: str) -> tuple[float, float, float, float] | None:
    # Sem "featureType=city" o Nominatim pode devolver como primeiro
    # resultado algo bem maior que a cidade (ex: "Brasília" batendo com
    # "Brasil", o país inteiro, por importância) — o que faz o Overpass
    # buscar num raio absurdo e estourar em timeout.
    resp = await client.get(
        NOMINATIM_URL,
        params={"q": cidade, "format": "json", "limit": 1, "featureType": "city"},
        headers={"User-Agent": USER_AGENT},
    )
    resp.raise_for_status()
    resultados = resp.json()
    if not resultados:
        # Cidade pequena pode não estar marcada como "city" no OSM; tenta
        # sem a restrição de tipo antes de desistir.
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


def _tipos_amenity_relevantes(termo: str) -> list[str]:
    """A maioria das clínicas não tem a especialidade no próprio nome
    cadastrado no OSM (ex: 'Clínica Dra. Fulana', não 'Ginecologia
    Fulana') — só filtrar por name~termo praticamente nunca acha nada pra
    especialidade médica. Complementa com o tipo de estabelecimento."""
    termo_lower = termo.lower()
    if any(p in termo_lower for p in ("odont", "dent")):
        return ["dentist"]
    if any(
        p in termo_lower
        for p in (
            "estétic",
            "estetic",
            "depila",
            "sobrancelha",
            "cílio",
            "cilio",
            "beleza",
            "podolog",
            "maquiagem",
            "micropigment",
        )
    ):
        return []  # tratado à parte via shop=beauty/hairdresser
    return ["doctors", "clinic", "hospital"]


def _montar_query_overpass(termo: str, bbox: tuple[float, float, float, float]) -> str:
    sul, oeste, norte, leste = bbox
    caixa = f"{sul},{oeste},{norte},{leste}"
    amenities = _tipos_amenity_relevantes(termo)

    clausulas = [
        f'node["name"~"{termo}",i]({caixa});',
        f'way["name"~"{termo}",i]({caixa});',
    ]
    if amenities:
        filtro = "|".join(amenities)
        clausulas += [
            f'node["amenity"~"^({filtro})$"]({caixa});',
            f'way["amenity"~"^({filtro})$"]({caixa});',
        ]
    else:
        clausulas += [
            f'node["shop"~"^(beauty|hairdresser)$"]({caixa});',
            f'way["shop"~"^(beauty|hairdresser)$"]({caixa});',
        ]

    corpo = "\n      ".join(clausulas)
    return f"""
    [out:json][timeout:15];
    (
      {corpo}
    );
    out center 100;
    """


def _rede_social_url(valor: str | None, dominio: str) -> str | None:
    """OSM às vezes guarda só o @handle (ex: 'otorrinobrasilia9'), às vezes
    a URL completa — normaliza pros dois casos."""
    if not valor:
        return None
    valor = valor.strip()
    if valor.startswith("http://") or valor.startswith("https://"):
        return valor
    handle = valor.lstrip("@")
    return f"https://www.{dominio}.com/{handle}"


def _somente_digitos(valor: str | None) -> str | None:
    if not valor:
        return None
    digitos = "".join(c for c in valor if c.isdigit())
    return digitos or None


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
        website = tags.get("website") or tags.get("contact:website")
        leads.append(
            {
                "nome": nome,
                "telefone": tags.get("phone") or tags.get("contact:phone"),
                "endereco": _montar_endereco(tags),
                "especialidade": termo,
                "place_id": f"osm-{el.get('type')}-{el.get('id')}",
                "link_perfil": website,
                "website": website,
                "instagram": _rede_social_url(tags.get("contact:instagram"), "instagram"),
                "facebook": _rede_social_url(tags.get("contact:facebook"), "facebook"),
                "email": tags.get("email") or tags.get("contact:email"),
                "whatsapp_direto": _somente_digitos(tags.get("contact:whatsapp")),
                "fonte": "osm",
            }
        )

    return leads
