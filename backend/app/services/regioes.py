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


# Algumas regiões do DF (Gama, Planaltina) têm cidade homônima logo do outro
# lado da divisa com Goiás (Novo Gama-GO, Planaltina-GO) — a Places API às
# vezes mistura. Filtra pelo estado no endereço formatado, que a Google
# sempre inclui (ex: "... - Brasília - DF, 70390-000, Brasil").
def descarta_fora_do_df(leads: list[dict], cidade: str) -> list[dict]:
    if cidade.strip().lower() not in REGIOES_METROPOLITANAS:
        return leads
    return [
        lead
        for lead in leads
        if not lead.get("endereco") or " - GO," not in lead["endereco"]
    ]
