from datetime import datetime, timedelta
from flask import render_template, request, redirect, url_for, flash, current_app
from app.movements import movements_bp
from app.extensions import db
from app.models import Movement, User, Part, Brand
from app.utils.pagination import paginate
from app.utils.formatters import parse_date, tempo_relativo
from app.utils.pdf import render_pdf_response
from sqlalchemy import or_
from sqlalchemy.orm import joinedload
import os

ITEMS_PER_PAGE = 50


@movements_bp.route("/")
def list_movements():
    dia = request.args.get("dia")
    
    if dia:
        dia_atual = parse_date(dia) or datetime.now()
    else:
        dia_atual = datetime.now()

    dia_inicio = datetime(dia_atual.year, dia_atual.month, dia_atual.day, 0, 0, 0)
    dia_fim = datetime(dia_atual.year, dia_atual.month, dia_atual.day, 23, 59, 59)

    user_id = request.args.get("user_id", type=int)
    part_id = request.args.get("part_id", type=int)
    status = request.args.get("status", "")

    # Otimização com joinedload para eliminar problemas N+1
    query = Movement.query.options(
        joinedload(Movement.user),
        joinedload(Movement.part).joinedload(Part.brand)
    ).filter(
        or_(
            (Movement.data_hora >= dia_inicio) & (Movement.data_hora <= dia_fim),
            (Movement.data_devolucao >= dia_inicio) & (Movement.data_devolucao <= dia_fim)
        )
    )

    if user_id:
        query = query.filter(Movement.user_id == user_id)
    if part_id:
        query = query.filter(Movement.part_id == part_id)
    if status == "aberto":
        query = query.filter(Movement.emprestimo_aberto.is_(True))
    elif status == "fechado":
        query = query.filter(Movement.emprestimo_aberto.is_(False))

    movements = paginate(query.order_by(Movement.data_hora.desc()), per_page=ITEMS_PER_PAGE)

    agora = datetime.now()
    for mov in movements.items:
        mov.tempo_relativo = tempo_relativo(mov.data_hora)
        minutos = (agora - mov.data_hora).total_seconds() / 60
        if minutos <= 5:
            mov.recent_class = "recent-strong"
        elif minutos <= 30:
            mov.recent_class = "recent-light"
        else:
            mov.recent_class = ""

    users = User.query.order_by(User.nome.asc()).all()
    parts = Part.query.options(joinedload(Part.brand)).order_by(Part.nome.asc()).all()

    dia_atual_fmt = dia_inicio.strftime("%d-%m-%Y")
    dia_anterior = (dia_inicio - timedelta(days=1)).strftime("%d-%m-%Y")
    dia_posterior = (dia_inicio + timedelta(days=1)).strftime("%d-%m-%Y")

    return render_template(
        "movements/list.html",
        movements=movements, 
        users=users, 
        parts=parts,
        dia_atual=dia_atual_fmt, 
        dia_navegacao=dia_atual_fmt,
        dia_anterior=dia_anterior, 
        dia_posterior=dia_posterior,
        user_id=user_id or "", 
        part_id=part_id or "", 
        status=status
    )


@movements_bp.route("/novo", methods=["GET", "POST"])
def create_movement():
    users = User.query.order_by(User.nome.asc()).all()
    parts = Part.query.options(joinedload(Part.brand)).order_by(Part.nome.asc()).all()

    if request.method == "POST":
        user_id = request.form.get("user_id")
        part_id = request.form.get("part_id")
        quantidade = request.form.get("quantidade", "1").strip()
        observacao = request.form.get("observacao", "").strip()
        
        if not user_id or not part_id or not quantidade:
            flash("Usuário, peça e quantidade são obrigatórios.", "danger")
            return render_template("movements/form.html", users=users, parts=parts)

        try:
            quantidade_int = int(quantidade)
            if quantidade_int <= 0:
                raise ValueError
        except ValueError:
            flash("Quantidade deve ser número inteiro positivo.", "danger")
            return render_template("movements/form.html", users=users, parts=parts)

        user = User.query.get(user_id)
        part = Part.query.get(part_id)
        if not user or not part:
            flash("Usuário ou peça inválidos.", "danger")
            return render_template("movements/form.html", users=users, parts=parts)

        if part.quantidade < quantidade_int:
            flash("Quantidade em estoque insuficiente.", "danger")
            return render_template("movements/form.html", users=users, parts=parts)

        movement = Movement(
            tipo="saida", 
            user=user, 
            part=part,
            quantidade=quantidade_int, 
            emprestimo_aberto=True,
            observacao=observacao, 
            data_hora=datetime.now()
        )

        part.quantidade -= quantidade_int
        db.session.add(movement)
        db.session.commit()
        flash("Movimentação registrada com sucesso!", "success")
        return redirect(url_for("movements.list_movements"))

    return render_template("movements/form.html", users=users, parts=parts)


@movements_bp.route("/scanner", methods=["POST"])
def create_movement_scanner():
    user_codigo = request.form.get("user_codigo", "").strip()
    part_codigo = request.form.get("part_codigo", "").strip()
    tipo_movimento = request.form.get("tipo_movimento", "saida").strip()

    if not user_codigo or not part_codigo:
        flash("Dados incompletos. Certifique-se de bipar o usuário e a peça.", "danger")
        return redirect(url_for("movements.list_movements"))

    user = User.query.filter_by(codigo=user_codigo).first()
    if not user:
        flash(f"Usuário com o código '{user_codigo}' não encontrado.", "danger")
        return redirect(url_for("movements.list_movements"))

    part = Part.query.filter_by(codigo=part_codigo).first()
    if not part:
        flash(f"Peça com o código '{part_codigo}' não encontrada.", "danger")
        return redirect(url_for("movements.list_movements"))

    if tipo_movimento == "saida":
        if part.quantidade < 1:
            flash(f"Estoque insuficiente para a peça: {part.nome}.", "warning")
            return redirect(url_for("movements.list_movements"))

        movement = Movement(
            tipo="saida", 
            user=user, 
            part=part,
            quantidade=1, 
            emprestimo_aberto=True,
            observacao="Retirada realizada via código de barras.", 
            data_hora=datetime.now()
        )
        part.quantidade -= 1
        db.session.add(movement)
        msg_sucesso = f"Sucesso! 1 un. de '{part.nome}' retirada por '{user.nome}'."

    else:
        # Busca a pendência mais antiga desta peça para fazer a baixa correta
        mov_aberto = Movement.query.filter_by(
            part_id=part.id, 
            emprestimo_aberto=True
        ).order_by(Movement.data_hora.asc()).first()

        if mov_aberto:
            usuario_original = mov_aberto.user.nome
            
            mov_aberto.emprestimo_aberto = False
            mov_aberto.data_devolucao = datetime.now()
            mov_aberto.devolvido_por = user.nome
            mov_aberto.observacao = (mov_aberto.observacao or "") + f"\nDevolução recebida por {user.nome} via código de barras."
            
            part.quantidade += mov_aberto.quantidade
            msg_sucesso = f"Devolução realizada! Peça '{part.nome}' (retirada por {usuario_original}) foi devolvida por '{user.nome}'."
        else:
            flash(f"Não há nenhuma retirada em aberto pendente para a peça '{part.nome}' no sistema.", "warning")
            return redirect(url_for("movements.list_movements"))

    db.session.commit()
    flash(msg_sucesso, "success")
    return redirect(url_for("movements.list_movements"))


@movements_bp.route("/ver/<int:id>")
def view_movement(id):
    mov = Movement.query.options(
        joinedload(Movement.user),
        joinedload(Movement.part).joinedload(Part.brand)
    ).get_or_404(id)
    return render_template("movements/view.html", mov=mov)


@movements_bp.route("/devolver/<int:id>", methods=["POST"])
def devolver(id):
    movement = Movement.query.get_or_404(id)
    devolvido_por = request.form.get("devolvido_por", "").strip()
    data_devolucao = request.form.get("data_devolucao")
    hora_devolucao = request.form.get("hora_devolucao")
    observacao = request.form.get("observacao", "").strip()

    if not devolvido_por or not data_devolucao or not hora_devolucao:
        flash("Preencha todos os campos obrigatórios.", "danger")
        return redirect(url_for("movements.list_movements"))

    try:
        data_hora_devolucao = datetime.strptime(f"{data_devolucao} {hora_devolucao}", "%Y-%m-%d %H:%M")
    except ValueError:
        flash("Formato de data ou hora de devolução inválido.", "danger")
        return redirect(url_for("movements.list_movements"))
    
    movement.emprestimo_aberto = False
    movement.data_devolucao = data_hora_devolucao
    movement.devolvido_por = devolvido_por
    if observacao:
        movement.observacao = (movement.observacao or "") + f"\nDevolução: {observacao}"
    movement.part.quantidade += movement.quantidade

    db.session.commit()
    flash("Devolução registrada com sucesso!", "success")
    return redirect(url_for("movements.list_movements"))


@movements_bp.route("/excluir/<int:id>")
def delete_movement(id):
    movement = Movement.query.get_or_404(id)
    if movement.emprestimo_aberto:
        movement.part.quantidade += movement.quantidade
    else:
        movement.part.quantidade -= movement.quantidade
    db.session.delete(movement)
    db.session.commit()
    flash("Movimentação excluída e estoque ajustado.", "success")
    return redirect(url_for("movements.list_movements"))


@movements_bp.route("/pdf/<dia>")
def pdf_movements(dia):
    dia_dt = parse_date(dia) or datetime.now()
    dia_inicio = datetime(dia_dt.year, dia_dt.month, dia_dt.day)
    dia_fim = dia_inicio + timedelta(days=1)
    
    movimentos = Movement.query.options(
        joinedload(Movement.user),
        joinedload(Movement.part).joinedload(Part.brand)
    ).filter(
        Movement.data_hora >= dia_inicio,
        Movement.data_hora < dia_fim
    ).order_by(Movement.data_hora.asc()).all()

    data_emissao = datetime.now().strftime("%d/%m/%Y %H:%M")
    html = render_template("movements/pdf.html", movimentos=movimentos, dia=dia, data_emissao=data_emissao)
    return render_pdf_response(
        html_content=html,
        filename=f"movimentacoes_{dia}.pdf",
        fallback_endpoint="movements.list_movements",
        fallback_args={"dia": dia}
    )


@movements_bp.route("/comprovante/<int:id>")
def comprovante(id):
    mov = Movement.query.options(
        joinedload(Movement.user),
        joinedload(Movement.part).joinedload(Part.brand)
    ).get_or_404(id)
    
    html = render_template("movements/comprovante.html", mov=mov)
    return render_pdf_response(
        html_content=html,
        filename=f"comprovante_{mov.id}.pdf",
        fallback_endpoint="movements.view_movement",
        fallback_args={"id": id}
    )


@movements_bp.route("/relatorio", methods=["GET"])
def relatorio_mensal():
    agora = datetime.now()
    ano = request.args.get("ano", type=int) or agora.year
    mes = request.args.get("mes", type=int)
    if not mes or mes < 1 or mes > 12:
        mes = agora.month

    inicio = datetime(ano, mes, 1)
    fim = (inicio + timedelta(days=32)).replace(day=1)

    movimentos = Movement.query.filter(
        Movement.data_hora >= inicio,
        Movement.data_hora < fim
    ).all()

    dias = {}
    for mov in movimentos:
        d = mov.data_hora.day
        dias[d] = dias.get(d, 0) + mov.quantidade

    labels = list(dias.keys())
    valores = list(dias.values())
    total_mes = sum(valores)
    total_dias_ativos = len(labels)

    return render_template(
        "movements/relatorio.html",
        labels=labels,
        valores=valores,
        total_mes=total_mes,
        total_dias_ativos=total_dias_ativos,
        ano=ano,
        mes=mes
    )
