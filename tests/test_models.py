from datetime import datetime
from app.extensions import db
from app.models import User, Part, Brand, Movement, Note

def test_create_brand_and_part(app):
    with app.app_context():
        brand = Brand(nome="Robust")
        db.session.add(brand)
        db.session.commit()

        part = Part(
            codigo="P001",
            nome="Adaptador 1/2 P 1/4",
            descricao="Adaptador industrial",
            quantidade=10,
            valor_custo=45.50,
            brand=brand
        )
        db.session.add(part)
        db.session.commit()

        retrieved = Part.query.filter_by(codigo="P001").first()
        assert retrieved is not None
        assert retrieved.brand.nome == "Robust"
        assert retrieved.marca_nome == "Robust"
        assert len(brand.parts) == 1

def test_part_without_brand(app):
    with app.app_context():
        part = Part(
            codigo="P002",
            nome="Parafuso Universal",
            quantidade=100,
            valor_custo=1.20
        )
        db.session.add(part)
        db.session.commit()

        retrieved = Part.query.filter_by(codigo="P002").first()
        assert retrieved.brand is None
        assert retrieved.marca_nome == ""

def test_movement_relationships(app):
    with app.app_context():
        user = User(codigo="U01", nome="Carlos Silva", email="carlos@empresa.com", telefone="11999999999", funcao="Mecânico")
        part = Part(codigo="P003", nome="Chave Sextavada", quantidade=5, valor_custo=20.0)
        db.session.add_all([user, part])
        db.session.commit()

        movement = Movement(tipo="saida", user=user, part=part, quantidade=2, emprestimo_aberto=True)
        db.session.add(movement)
        db.session.commit()

        assert len(user.movements) == 1
        assert len(part.movements) == 1
        assert movement.user.nome == "Carlos Silva"
        assert movement.part.nome == "Chave Sextavada"
