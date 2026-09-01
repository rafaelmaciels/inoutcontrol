from flask import render_template, request, redirect, url_for, flash, jsonify
from app.users import users_bp
from app.extensions import db
from app.models import User
from app.utils.pagination import paginate   # <-- paginação geral
from app.utils.formatters import padronizar_codigo, gerar_proximo_codigo_usuario
from sqlalchemy import or_

ITEMS_PER_PAGE = 10


# ============================ # API GERAR CÓDIGO AUTOMÁTICO DE USUÁRIO # ============================
@users_bp.route("/api/gerar-codigo")
def api_gerar_codigo():
    """Retorna um código único sequencial de usuário gerado automaticamente no padrão oficial (USR-XXX)."""
    return jsonify({"codigo": gerar_proximo_codigo_usuario()})


# ============================ # API AUTOCOMPLETE DE USUÁRIOS (BUSCA FIEL POR INICIAIS) # ============================
@users_bp.route("/api/autocomplete")
def autocomplete_users():
    """
    Retorna sugestões JSON para autocomplete fiel onde o nome, código ou e-mail começa com as iniciais digitadas.
    Exemplo: 'CAR' retorna 'Carlos Eduardo', 'USR-002', etc.
    """
    termo = request.args.get("q", "").strip()
    if not termo:
        return jsonify([])

    starts_like = f"{termo}%"
    users = User.query.filter(
        or_(
            User.nome.ilike(starts_like),
            User.codigo.ilike(starts_like),
            User.email.ilike(starts_like),
            User.funcao.ilike(starts_like)
        )
    ).order_by(User.nome.asc()).limit(10).all()

    results = []
    for u in users:
        results.append({
            "id": u.id,
            "codigo": u.codigo,
            "nome": u.nome,
            "email": u.email,
            "funcao": u.funcao or "Operador",
            "telefone": u.telefone or ""
        })

    return jsonify(results)


@users_bp.route("/")
def list_users():
    termo = request.args.get("q", "").strip()

    query = User.query
    if termo:
        like = f"%{termo}%"
        query = query.filter(
            (User.nome.ilike(like)) |
            (User.email.ilike(like)) |
            (User.telefone.ilike(like)) |
            (User.funcao.ilike(like)) |
            (User.codigo.ilike(like))   # permite buscar também pelo código
        )

    # Paginação geral
    users = paginate(query.order_by(User.nome.asc()), per_page=ITEMS_PER_PAGE)

    return render_template("users/list.html", users=users, termo=termo)


@users_bp.route("/novo", methods=["GET", "POST"])
def create_user():
    if request.method == "POST":
        codigo = padronizar_codigo(request.form.get("codigo", ""))
        
        # Se não fornecido ou vazio, gera automaticamente no padrão oficial (USR-XXX)
        if not codigo:
            codigo = gerar_proximo_codigo_usuario()

        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        telefone = request.form.get("telefone", "").strip()
        funcao = request.form.get("funcao", "").strip()

        if not nome or not email or not telefone or not funcao:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("users/form.html", user=None, codigo_sugerido=gerar_proximo_codigo_usuario())

        # Verifica se já existe usuário com mesmo código
        existente_codigo = User.query.filter_by(codigo=codigo).first()
        if existente_codigo:
            flash(f"Já existe um usuário com o código '{codigo}'.", "danger")
            return render_template("users/form.html", user=None, codigo_sugerido=gerar_proximo_codigo_usuario())

        # Verifica se já existe usuário com mesmo e-mail
        existente_email = User.query.filter_by(email=email).first()
        if existente_email:
            flash("Já existe um usuário com esse e-mail.", "danger")
            return render_template("users/form.html", user=None, codigo_sugerido=gerar_proximo_codigo_usuario())

        user = User(codigo=codigo, nome=nome, email=email, telefone=telefone, funcao=funcao)
        db.session.add(user)
        db.session.commit()
        flash(f"Usuário '{nome}' (Cód: {codigo}) cadastrado com sucesso!", "success")
        return redirect(url_for("users.list_users"))

    codigo_sugerido = gerar_proximo_codigo_usuario()
    return render_template("users/form.html", user=None, codigo_sugerido=codigo_sugerido)


@users_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def edit_user(id):
    user = User.query.get_or_404(id)

    if request.method == "POST":
        codigo = padronizar_codigo(request.form.get("codigo", ""))
        nome = request.form.get("nome", "").strip()
        email = request.form.get("email", "").strip()
        telefone = request.form.get("telefone", "").strip()
        funcao = request.form.get("funcao", "").strip()

        if not codigo or not nome or not email or not telefone or not funcao:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("users/form.html", user=user)

        # Verifica se já existe outro usuário com mesmo código
        existente_codigo = User.query.filter(User.codigo == codigo, User.id != user.id).first()
        if existente_codigo:
            flash(f"Já existe outro usuário com o código '{codigo}'.", "danger")
            return render_template("users/form.html", user=user)

        # Verifica se já existe outro usuário com mesmo e-mail
        existente_email = User.query.filter(User.email == email, User.id != user.id).first()
        if existente_email:
            flash("Já existe outro usuário com esse e-mail.", "danger")
            return render_template("users/form.html", user=user)

        user.codigo = codigo
        user.nome = nome
        user.email = email
        user.telefone = telefone
        user.funcao = funcao

        db.session.commit()
        flash("Usuário atualizado com sucesso!", "success")
        return redirect(url_for("users.list_users"))

    return render_template("users/form.html", user=user)


@users_bp.route("/excluir/<int:id>")
def delete_user(id):
    user = User.query.get_or_404(id)

    if user.movements:
        flash("Não é possível excluir usuário com movimentações vinculadas.", "danger")
        return redirect(url_for("users.list_users"))

    db.session.delete(user)
    db.session.commit()
    flash("Usuário excluído com sucesso!", "success")
    return redirect(url_for("users.list_users"))
