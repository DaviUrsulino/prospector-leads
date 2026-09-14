def test_criar_busca_enriquece_leads_com_website(client, monkeypatch):
    async def fake_enriquecer_leads(leads):
        return [
            {
                **lead,
                "instagram": "https://instagram.com/exemplo",
                "linkedin": None,
                "facebook": None,
                "email": "contato@exemplo.com",
                "whatsapp_direto": None,
            }
            for lead in leads
        ]

    monkeypatch.setattr(
        "app.routers.buscas.enriquecer_leads", fake_enriquecer_leads
    )

    resp = client.post(
        "/buscas",
        json={"cidade": "São Paulo", "termos": ["dentista"], "quantidade_alvo": 2},
    )
    assert resp.status_code == 200
    leads = resp.json()["leads"]
    assert all(lead["instagram"] == "https://instagram.com/exemplo" for lead in leads)
    assert all(lead["email"] == "contato@exemplo.com" for lead in leads)
    assert all(lead["fonte"] == "google_places" for lead in leads)


def test_criar_busca_usa_fallback_osm_quando_places_nao_completa(client, monkeypatch):
    async def fake_buscar_leads(cidade, termo, quantidade_alvo):
        return []

    async def fake_buscar_leads_osm(cidade, termo, quantidade):
        return [
            {
                "nome": f"{termo} OSM {i}",
                "telefone": None,
                "endereco": None,
                "especialidade": termo,
                "place_id": f"osm-node-{i}",
                "link_perfil": None,
                "website": None,
                "fonte": "osm",
            }
            for i in range(quantidade)
        ]

    monkeypatch.setattr("app.routers.buscas.buscar_leads", fake_buscar_leads)
    monkeypatch.setattr("app.routers.buscas.buscar_leads_osm", fake_buscar_leads_osm)

    resp = client.post(
        "/buscas",
        json={"cidade": "São Paulo", "termos": ["dentista"], "quantidade_alvo": 3},
    )
    assert resp.status_code == 200
    leads = resp.json()["leads"]
    assert len(leads) == 3
    assert all(lead["fonte"] == "osm" for lead in leads)


def test_criar_busca_expande_pra_regioes_quando_ainda_falta(client, monkeypatch):
    async def fake_buscar_leads(cidade, termo, quantidade_alvo):
        if cidade == "Brasília":
            return []
        return [
            {
                "nome": f"Clínica {cidade} {i}",
                "telefone": f"+55 61 9{i:04d}-0000",
                "endereco": cidade,
                "especialidade": termo,
                "place_id": f"place-{cidade}-{i}",
                "link_perfil": None,
                "website": None,
                "fonte": "google_places",
            }
            for i in range(min(quantidade_alvo, 5))
        ]

    async def fake_buscar_leads_osm(cidade, termo, quantidade):
        return []

    monkeypatch.setattr("app.routers.buscas.buscar_leads", fake_buscar_leads)
    monkeypatch.setattr("app.routers.buscas.buscar_leads_osm", fake_buscar_leads_osm)

    resp = client.post(
        "/buscas",
        json={"cidade": "Brasília", "termos": ["urologia"], "quantidade_alvo": 5},
    )
    assert resp.status_code == 200
    leads = resp.json()["leads"]
    assert len(leads) == 5
    assert all("Ceilândia" in lead["endereco"] for lead in leads)


def test_criar_busca_retorna_leads_mockados(client):
    resp = client.post(
        "/buscas",
        json={"cidade": "São Paulo", "termos": ["dentista"], "quantidade_alvo": 5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["cidade"] == "São Paulo"
    assert len(body["leads"]) == 5
    assert all(lead["especialidade"] == "dentista" for lead in body["leads"])


def test_criar_busca_aceita_especialidade_livre(client):
    resp = client.post(
        "/buscas",
        json={"cidade": "São Paulo", "termos": ["ortopedista"], "quantidade_alvo": 3},
    )
    assert resp.status_code == 200
    assert resp.json()["termo"] == "ortopedista"


def test_criar_busca_com_termo_curto_retorna_422(client):
    resp = client.post(
        "/buscas",
        json={"cidade": "São Paulo", "termos": ["a"], "quantidade_alvo": 5},
    )
    assert resp.status_code == 422


def test_criar_busca_sem_nenhum_termo_retorna_422(client):
    resp = client.post(
        "/buscas",
        json={"cidade": "São Paulo", "termos": [], "quantidade_alvo": 5},
    )
    assert resp.status_code == 422


def test_criar_busca_com_multiplas_especialidades_combina_resultado(client):
    resp = client.post(
        "/buscas",
        json={
            "cidade": "São Paulo",
            "termos": ["ortodontia", "endodontia"],
            "quantidade_alvo": 6,
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["termo"] == "ortodontia, endodontia"
    especialidades = {lead["especialidade"] for lead in body["leads"]}
    assert especialidades == {"ortodontia", "endodontia"}
    assert len(body["leads"]) == 6


def test_criar_busca_nao_repete_lead_ja_encontrado_antes(client):
    primeira = client.post(
        "/buscas",
        json={"cidade": "Recife", "termos": ["dentista"], "quantidade_alvo": 5},
    ).json()
    assert len(primeira["leads"]) == 5

    segunda = client.post(
        "/buscas",
        json={"cidade": "Recife", "termos": ["dentista"], "quantidade_alvo": 5},
    ).json()
    # Mock é determinístico pra mesma cidade+termo: a segunda busca acha
    # exatamente os mesmos estabelecimentos, então a deduplicação deve
    # descartar todos.
    assert segunda["leads"] == []


def test_listar_e_obter_busca(client):
    criada = client.post(
        "/buscas",
        json={"cidade": "Brasília", "termos": ["medico"], "quantidade_alvo": 3},
    ).json()

    listagem = client.get("/buscas")
    assert listagem.status_code == 200
    assert any(b["id"] == criada["id"] for b in listagem.json())

    detalhe = client.get(f"/buscas/{criada['id']}")
    assert detalhe.status_code == 200
    assert len(detalhe.json()["leads"]) == 3


def test_busca_inexistente_retorna_404(client):
    resp = client.get("/buscas/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


def test_estatisticas(client):
    client.post(
        "/buscas",
        json={"cidade": "Salvador", "termos": ["biomedico"], "quantidade_alvo": 4},
    )
    resp = client.get("/buscas/estatisticas")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_buscas"] == 1
    assert body["total_leads"] == 4
    assert body["pct_leads_com_telefone"] == 100.0
    assert body["total_favoritos"] == 0
    assert len(body["ultimas_buscas"]) == 1


def test_alternar_favorito(client):
    criada = client.post(
        "/buscas",
        json={"cidade": "Fortaleza", "termos": ["medico"], "quantidade_alvo": 1},
    ).json()
    lead_id = criada["leads"][0]["id"]

    resp = client.patch(f"/buscas/{criada['id']}/leads/{lead_id}/favorito")
    assert resp.status_code == 200
    assert resp.json()["favorito"] is True

    resp = client.patch(f"/buscas/{criada['id']}/leads/{lead_id}/favorito")
    assert resp.json()["favorito"] is False


def test_excluir_busca(client):
    criada = client.post(
        "/buscas",
        json={"cidade": "Porto Alegre", "termos": ["esteticista"], "quantidade_alvo": 1},
    ).json()

    resp = client.delete(f"/buscas/{criada['id']}")
    assert resp.status_code == 204
    assert client.get(f"/buscas/{criada['id']}").status_code == 404


def test_export_csv(client):
    criada = client.post(
        "/buscas",
        json={"cidade": "Curitiba", "termos": ["esteticista"], "quantidade_alvo": 2},
    ).json()

    resp = client.get(f"/buscas/{criada['id']}/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert (
        "nome,telefone,endereco,especialidade,link_perfil,favorito,"
        "website,instagram,linkedin,facebook,email,whatsapp_direto,fonte" in resp.text
    )
