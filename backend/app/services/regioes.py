# "Brasília" sozinho, na Places API, tende a cobrir só o Plano Piloto —
# as cidades-satélite (regiões administrativas do DF) são tratadas como
# lugares distintos. Quando a busca principal não completa a quantidade
# pedida, tentamos essas regiões também antes de desistir.
REGIOES_METROPOLITANAS: dict[str, list[str]] = {
    "brasília": [
        "Ceilândia, Brasília",
        "Taguatinga, Brasília",
        "Águas Claras, Brasília",
        "Sobradinho, Brasília",
        "Gama, Brasília",
        "Planaltina, Brasília",
        "Samambaia, Brasília",
        "Guará, Brasília",
    ],
    "brasilia": [
        "Ceilândia, Brasília",
        "Taguatinga, Brasília",
        "Águas Claras, Brasília",
        "Sobradinho, Brasília",
        "Gama, Brasília",
        "Planaltina, Brasília",
        "Samambaia, Brasília",
        "Guará, Brasília",
    ],
}


def regioes_extras(cidade: str) -> list[str]:
    return REGIOES_METROPOLITANAS.get(cidade.strip().lower(), [])
