from app.extensions import db
from app.models import User, Part, Movement

def test_movement_saida_and_devolucao(client, app):
    with app.app_context():
        user = User(codigo="U02", nome="Marcos Souza", email="marcos@teste.com", telefone="11988887777", funcao="Técnico")
        part = Part(codigo="P100", nome="Rolamento 6204", quantidade=10, valor_custo=30.0)
        db.session.add_all([user, part])
        db.session.commit()
        user_id = user.id
        part_id = part.id

    # 1. Cria saída
    res_saida = client.post("/movimentacoes/novo", data={
        "user_id": user_id,
        "part_id": part_id,
        "quantidade": "3",
        "observacao": "Manutenção preventiva"
    }, follow_redirects=True)

    assert res_saida.status_code == 200
    with app.app_context():
        part_check = Part.query.get(part_id)
        assert part_check.quantidade == 7  # 10 - 3 = 7
        mov = Movement.query.filter_by(part_id=part_id, emprestimo_aberto=True).first()
        assert mov is not None
        assert mov.quantidade == 3
        mov_id = mov.id

    # 2. Registra devolução
    res_dev = client.post(f"/movimentacoes/devolver/{mov_id}", data={
        "devolvido_por": "Marcos Souza",
        "data_devolucao": "2026-08-31",
        "hora_devolucao": "15:30",
        "observacao": "Devolvido em perfeito estado"
    }, follow_redirects=True)

    assert res_dev.status_code == 200
    with app.app_context():
        part_check = Part.query.get(part_id)
        assert part_check.quantidade == 10  # 7 + 3 = 10
        mov_check = Movement.query.get(mov_id)
        assert mov_check.emprestimo_aberto is False
        assert mov_check.devolvido_por == "Marcos Souza"

def test_movement_insufficient_stock(client, app):
    with app.app_context():
        user = User(codigo="U03", nome="Ana Lima", email="ana@teste.com", telefone="11977776666", funcao="Operadora")
        part = Part(codigo="P101", nome="Broca Aço Rápido", quantidade=2, valor_custo=10.0)
        db.session.add_all([user, part])
        db.session.commit()
        user_id = user.id
        part_id = part.id

    res = client.post("/movimentacoes/novo", data={
        "user_id": user_id,
        "part_id": part_id,
        "quantidade": "5"
    }, follow_redirects=True)

    assert res.status_code == 200
    assert b"Quantidade em estoque insuficiente." in res.data
    with app.app_context():
        part_check = Part.query.get(part_id)
        assert part_check.quantidade == 2  # Estoque inalterado
