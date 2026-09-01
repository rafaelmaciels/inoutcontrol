from app.extensions import db
from app.models import Part, Brand

def test_list_parts_and_search_by_brand(client, app):
    with app.app_context():
        brand1 = Brand(nome="Albuquerque Diesel")
        brand2 = Brand(nome="Robust")
        db.session.add_all([brand1, brand2])
        db.session.commit()

        p1 = Part(codigo="7906", nome="22 DE ENCAIXE SEXTAVADA", quantidade=15, valor_custo=35.0, brand=brand1)
        p2 = Part(codigo="7025", nome="ADAPTADOR 1/2 P 1/4", quantidade=8, valor_custo=22.0, brand=brand2)
        p3 = Part(codigo="1001", nome="PORCA SIMPLES", quantidade=0, valor_custo=0.50)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

    # Listagem geral
    res = client.get("/pecas/")
    assert res.status_code == 200
    assert b"22 DE ENCAIXE SEXTAVADA" in res.data
    assert b"Albuquerque Diesel" in res.data
    assert b"Robust" in res.data
    assert b"Em falta" in res.data

    # Busca pela marca
    res_search = client.get("/pecas/?q=Albuquerque")
    assert res_search.status_code == 200
    assert b"22 DE ENCAIXE SEXTAVADA" in res_search.data
    assert b"ADAPTADOR 1/2 P 1/4" not in res_search.data

def test_create_part_with_brand(client, app):
    res = client.post("/pecas/novo", data={
        "codigo": "7907",
        "nome": "24 DE ENCAIXE SEXTAVADA",
        "descricao": "Encaixe reforçado",
        "quantidade": "12",
        "valor_custo": "40,50",
        "marca": "Albuquerque Diesel"
    }, follow_redirects=True)

    assert res.status_code == 200
    assert "cadastrada com sucesso!" in res.get_data(as_text=True)

    with app.app_context():
        part = Part.query.filter_by(codigo="7907").first()
        assert part is not None
        assert part.valor_custo == 40.50
        assert part.brand is not None
        assert part.brand.nome == "Albuquerque Diesel"

def test_edit_part_and_change_brand(client, app):
    with app.app_context():
        brand = Brand(nome="Vonder")
        part = Part(codigo="5555", nome="Chave Fenda", quantidade=3, valor_custo=15.0, brand=brand)
        db.session.add_all([brand, part])
        db.session.commit()
        part_id = part.id

    res = client.post(f"/pecas/editar/{part_id}", data={
        "codigo": "5555",
        "nome": "Chave Fenda Imantada",
        "descricao": "Ponta imantada",
        "quantidade": "5",
        "valor_custo": "18.00",
        "marca": "Gedore"
    }, follow_redirects=True)

    assert res.status_code == 200
    with app.app_context():
        updated = Part.query.get(part_id)
        assert updated.nome == "Chave Fenda Imantada"
        assert updated.quantidade == 5
        assert updated.brand.nome == "Gedore"

def test_parts_autocomplete_faithful_prefix(client, app):
    with app.app_context():
        p1 = Part(codigo="ALI-01", nome="ALICATE UNIVERSAL", quantidade=10, valor_custo=30.0)
        p2 = Part(codigo="ALI-02", nome="ALICATE DE PRESSAO", quantidade=5, valor_custo=45.0)
        p3 = Part(codigo="CHV-01", nome="CHAVE ALEN", quantidade=20, valor_custo=10.0)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

    # Busca por "ALI" (deve trazer somente os que começam com ALI)
    res = client.get("/pecas/api/autocomplete?q=ALI")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2
    nomes = [item["nome"] for item in data]
    assert "ALICATE UNIVERSAL" in nomes
    assert "ALICATE DE PRESSAO" in nomes
    assert "CHAVE ALEN" not in nomes

def test_auto_generate_part_code_and_prevent_duplicate(client, app):
    # 1. API de geração de código
    res_api = client.get("/pecas/api/gerar-codigo")
    assert res_api.status_code == 200
    cod = res_api.get_json()["codigo"]
    assert len(cod) >= 4 and cod.isdigit()

    # 2. Tela /pecas/novo traz o código pré-gerado
    res_get = client.get("/pecas/novo")
    assert res_get.status_code == 200
    assert cod in res_get.get_data(as_text=True)

    # 3. Cadastro sem informar código (gera automaticamente)
    res_post = client.post("/pecas/novo", data={
        "nome": "SOQUETE IMPACTO 19MM",
        "codigo": "",
        "quantidade": "10",
        "valor_custo": "25.00"
    }, follow_redirects=True)
    assert res_post.status_code == 200
    assert "cadastrada com sucesso!" in res_post.get_data(as_text=True)

    with app.app_context():
        p = Part.query.filter_by(nome="SOQUETE IMPACTO 19MM").first()
        assert p is not None
        assert p.codigo == cod

    # 4. Tentativa de cadastro com código duplicado deve ser bloqueada
    res_dup = client.post("/pecas/novo", data={
        "nome": "OUTRA PECA MESMO CODIGO",
        "codigo": cod,
        "quantidade": "1",
        "valor_custo": "10.00"
    }, follow_redirects=True)
    dup_text = res_dup.get_data(as_text=True)
    assert cod in dup_text
    assert "com esse" in dup_text or "com o" in dup_text or "existe" in dup_text


