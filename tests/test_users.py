from app.extensions import db
from app.models import User, Part, Movement

def test_user_crud(client, app):
    # Criar usuário
    res = client.post("/usuarios/novo", data={
        "codigo": "USR-001",
        "nome": "Roberto Carlos",
        "email": "roberto@empresa.com",
        "telefone": "11988880000",
        "funcao": "Supervisor"
    }, follow_redirects=True)

    assert res.status_code == 200
    assert "cadastrado com sucesso!" in res.get_data(as_text=True)

    with app.app_context():
        u = User.query.filter_by(codigo="USR-001").first()
        assert u is not None
        user_id = u.id

    # Editar usuário
    res_edit = client.post(f"/usuarios/editar/{user_id}", data={
        "codigo": "USR-001",
        "nome": "Roberto Carlos Silva",
        "email": "roberto.silva@empresa.com",
        "telefone": "11988880000",
        "funcao": "Gerente"
    }, follow_redirects=True)

    assert res_edit.status_code == 200
    with app.app_context():
        u_edit = User.query.get(user_id)
        assert u_edit.nome == "Roberto Carlos Silva"
        assert u_edit.funcao == "Gerente"

def test_cannot_delete_user_with_movements(client, app):
    with app.app_context():
        user = User(codigo="USR-002", nome="Juliana Dias", email="juliana@teste.com", telefone="11911112222", funcao="Estoquista")
        part = Part(codigo="P999", nome="Disco de Corte", quantidade=20, valor_custo=8.0)
        db.session.add_all([user, part])
        db.session.commit()

        mov = Movement(tipo="saida", user=user, part=part, quantidade=1)
        db.session.add(mov)
        db.session.commit()
        user_id = user.id

    res_del = client.get(f"/usuarios/excluir/{user_id}", follow_redirects=True)
    assert res_del.status_code == 200
    assert "moviment" in res_del.get_data(as_text=True)

    with app.app_context():
        u_check = User.query.get(user_id)
        assert u_check is not None

def test_auto_generate_user_code_and_prevent_duplicate(client, app):
    # 1. API de geração de código de usuário
    res_api = client.get("/usuarios/api/gerar-codigo")
    assert res_api.status_code == 200
    cod = res_api.get_json()["codigo"]
    assert cod.startswith("USR-")

    # 2. Tela /usuarios/novo traz o código pré-gerado
    res_get = client.get("/usuarios/novo")
    assert res_get.status_code == 200
    assert cod in res_get.get_data(as_text=True)

    # 3. Cadastro sem informar código (deve gerar automaticamente)
    res_post = client.post("/usuarios/novo", data={
        "codigo": "",
        "nome": "Fernando Souza",
        "email": "fernando.souza@empresa.com",
        "telefone": "(11) 98765-4321",
        "funcao": "Assistente de Estoque"
    }, follow_redirects=True)
    assert res_post.status_code == 200
    assert "cadastrado com sucesso!" in res_post.get_data(as_text=True)

    with app.app_context():
        u = User.query.filter_by(email="fernando.souza@empresa.com").first()
        assert u is not None
        assert u.codigo == cod

    # 4. Tentativa de cadastro com código duplicado deve ser bloqueada
    res_dup = client.post("/usuarios/novo", data={
        "codigo": cod,
        "nome": "Outro Fernando",
        "email": "outro.fernando@empresa.com",
        "telefone": "(11) 98765-4321",
        "funcao": "Operador"
    }, follow_redirects=True)
    dup_text = res_dup.get_data(as_text=True)
    assert cod in dup_text
    assert "com o" in dup_text or "com esse" in dup_text or "existe" in dup_text

def test_users_autocomplete_faithful_prefix(client, app):
    with app.app_context():
        u1 = User(codigo="USR-010", nome="CARLOS ALBERTO", email="carlos.alberto@empresa.com", telefone="11999991111", funcao="Mecânico")
        u2 = User(codigo="USR-011", nome="CARLOS EDUARDO", email="carlos.eduardo@empresa.com", telefone="11999992222", funcao="Supervisor")
        u3 = User(codigo="USR-012", nome="MARCELO COSTA", email="marcelo@empresa.com", telefone="11999993333", funcao="Operador")
        db.session.add_all([u1, u2, u3])
        db.session.commit()

    # Busca por "CAR" (deve trazer somente os usuários iniciando com CAR)
    res = client.get("/usuarios/api/autocomplete?q=CAR")
    assert res.status_code == 200
    data = res.get_json()
    assert len(data) == 2
    nomes = [item["nome"] for item in data]
    assert "CARLOS ALBERTO" in nomes
    assert "CARLOS EDUARDO" in nomes
    assert "MARCELO COSTA" not in nomes


