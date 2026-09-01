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
    assert b"Usu\xc3\xa1rio cadastrado com sucesso!" in res.data

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
    assert b"N\xc3\xa3o \xc3\xa9 poss\xc3\xadvel excluir usu\xc3\xa1rio com movimenta\xc3\xa7\xc3\xb5es vinculadas." in res_del.data

    with app.app_context():
        u_check = User.query.get(user_id)
        assert u_check is not None
