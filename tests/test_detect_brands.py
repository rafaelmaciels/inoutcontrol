from app.extensions import db
from app.models import Part
from scripts.detect_brands import analyze_parts

def test_detect_brands_script(app):
    with app.app_context():
        p1 = Part(codigo="7906", nome="22 DE ENCAIXE SEXTAVADA", descricao="Item fornecido por ALBUQUERQUE DIESEL", quantidade=10, valor_custo=30.0)
        p2 = Part(codigo="7025", nome="ADAPTADOR 1/2 P 1/4", descricao="Adaptador marca ROBUST linha industrial", quantidade=5, valor_custo=15.0)
        p3 = Part(codigo="9999", nome="PARAFUSO SEXTAVADO", descricao="Sem especificacao", quantidade=100, valor_custo=1.0)
        db.session.add_all([p1, p2, p3])
        db.session.commit()

        analysis = analyze_parts(app)
        assert len(analysis) == 3

        item1 = next(item for item in analysis if item["codigo"] == "7906")
        assert item1["marca"] == "ALBUQUERQUE DIESEL"
        assert item1["confianca"] == "ALTA"

        item2 = next(item for item in analysis if item["codigo"] == "7025")
        assert item2["marca"] == "ROBUST"
        assert item2["confianca"] == "ALTA"

        item3 = next(item for item in analysis if item["codigo"] == "9999")
        assert item3["marca"] == "Não identificada"
        assert item3["confianca"] == "N/A"
