from flask import render_template
from sqlalchemy import func
from sqlalchemy.orm import joinedload
from app.dashboard import dashboard_bp
from app.models import Movement, Part, User, Note, Brand

@dashboard_bp.route("/")
def index():
    # Últimas movimentações com joinedload para máxima performance
    ultimas_movimentacoes = (
        Movement.query
        .options(
            joinedload(Movement.user),
            joinedload(Movement.part).joinedload(Part.brand)
        )
        .order_by(Movement.data_hora.desc())
        .limit(10)
        .all()
    )

    # Empréstimos abertos
    emprestimos_abertos = (
        Movement.query
        .options(
            joinedload(Movement.user),
            joinedload(Movement.part).joinedload(Part.brand)
        )
        .filter_by(emprestimo_aberto=True, tipo="saida")
        .all()
    )

    # Totais
    total_usuarios = User.query.count()
    total_pecas = Part.query.count()
    total_movimentacoes = Movement.query.count()
    total_notas = Note.query.count()

    # Baixo estoque — apenas peças realmente críticas (<= 2 unidades)
    baixo_estoque = (
        Part.query
        .options(joinedload(Part.brand))
        .filter(Part.quantidade <= 2)
        .order_by(Part.quantidade.asc())
        .limit(5)
        .all()
    )

    # Peças mais movimentadas
    top_pecas = (
        Movement.query
        .with_entities(Part.nome, func.sum(Movement.quantidade).label("total"))
        .join(Part, Movement.part_id == Part.id)
        .group_by(Part.nome)
        .order_by(func.sum(Movement.quantidade).desc())
        .limit(5)
        .all()
    )

    labels = [p[0] for p in top_pecas]
    valores = [int(p[1]) for p in top_pecas]

    return render_template(
        "dashboard/index.html",
        ultimas_movimentacoes=ultimas_movimentacoes,
        emprestimos_abertos=emprestimos_abertos,
        total_usuarios=total_usuarios,
        total_pecas=total_pecas,
        total_movimentacoes=total_movimentacoes,
        total_notas=total_notas,
        baixo_estoque=baixo_estoque,
        chart_labels=labels,
        chart_values=valores,
    )