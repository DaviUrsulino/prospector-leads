def test_criar_busca_retorna_leads_mockados(client):
    resp = client.post(
        "/buscas",
        json={"cidade": "São Paulo", "termo": "dentista", "quantidade_alvo": 5},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["cidade"] == "São Paulo"
    assert len(body["leads"]) == 5
    assert all(lead["especialidade"] == "dentista" for lead in body["leads"])


def test_criar_busca_com_termo_invalido_retorna_422(client):
    resp = client.post(
        "/buscas",
        json={"cidade": "São Paulo", "termo": "veterinario", "quantidade_alvo": 5},
    )
    assert resp.status_code == 422


def test_listar_e_obter_busca(client):
    criada = client.post(
        "/buscas",
        json={"cidade": "Brasília", "termo": "medico", "quantidade_alvo": 3},
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
        json={"cidade": "Salvador", "termo": "biomedico", "quantidade_alvo": 4},
    )
    resp = client.get("/buscas/estatisticas")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total_buscas"] == 1
    assert body["total_leads"] == 4
    assert body["pct_leads_com_telefone"] == 100.0
    assert len(body["ultimas_buscas"]) == 1


def test_export_csv(client):
    criada = client.post(
        "/buscas",
        json={"cidade": "Curitiba", "termo": "esteticista", "quantidade_alvo": 2},
    ).json()

    resp = client.get(f"/buscas/{criada['id']}/export")
    assert resp.status_code == 200
    assert resp.headers["content-type"].startswith("text/csv")
    assert "nome,telefone,endereco,especialidade,link_perfil" in resp.text
