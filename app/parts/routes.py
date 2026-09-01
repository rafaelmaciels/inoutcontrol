from flask import render_template, request, redirect, url_for, flash, current_app, jsonify
from app.parts import parts_bp
from app.extensions import db
from app.models import Part, Brand
from app.utils.pagination import paginate
from app.utils.formatters import allowed_file
from app.utils.pdf import render_pdf_response
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload

import qrcode
import base64
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
import os
from datetime import datetime
from werkzeug.utils import secure_filename

ITEMS_PER_PAGE = 10


# ============================ # API AUTOCOMPLETE DE PEÇAS (BUSCA FIEL POR INICIAIS) # ============================
@parts_bp.route("/api/autocomplete")
def autocomplete_parts():
    """
    Retorna sugestões JSON para autocomplete fiel onde o nome ou código começa com as iniciais digitadas.
    Exemplo: 'ALI' retorna itens começando com 'ALI...'.
    """
    termo = request.args.get("q", "").strip()
    if not termo:
        return jsonify([])

    starts_like = f"{termo}%"
    parts = Part.query.outerjoin(Brand, Part.brand_id == Brand.id).options(
        joinedload(Part.brand)
    ).filter(
        or_(
            Part.nome.ilike(starts_like),
            Part.codigo.ilike(starts_like)
        )
    ).order_by(Part.nome.asc()).limit(10).all()

    results = []
    for p in parts:
        results.append({
            "id": p.id,
            "codigo": p.codigo,
            "nome": p.nome,
            "marca": p.marca_nome,
            "quantidade": p.quantidade,
            "valor_custo": p.valor_custo or 0.0
        })

    return jsonify(results)


# ============================ # LISTAR PEÇAS # ============================
@parts_bp.route("/")
def list_parts():
    termo = request.args.get("q", "").strip()

    query = Part.query.outerjoin(Brand, Part.brand_id == Brand.id).options(joinedload(Part.brand))
    if termo:
        starts_like = f"{termo}%"
        query = query.filter(
            or_(
                Part.nome.ilike(starts_like),
                Part.codigo.ilike(starts_like),
                Brand.nome.ilike(starts_like)
            )
        )

    # Cálculo eficiente do custo total dos itens filtrados
    total_custo_estoque = query.with_entities(
        func.sum(Part.quantidade * Part.valor_custo)
    ).scalar() or 0.0

    parts = paginate(query.order_by(Part.nome.asc()), per_page=ITEMS_PER_PAGE)

    for p in parts.items:
        p.em_falta = (p.quantidade == 0)

    return render_template(
        "parts/list.html", 
        parts=parts, 
        termo=termo, 
        total_custo_estoque=total_custo_estoque
    )


# ============================ # NOVA PEÇA # ============================
@parts_bp.route("/novo", methods=["GET", "POST"])
def create_part():
    marcas = Brand.query.order_by(Brand.nome.asc()).all()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        codigo = request.form.get("codigo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        quantidade = request.form.get("quantidade", "").strip()
        valor_custo = request.form.get("valor_custo", "").strip()
        marca_nome = request.form.get("marca", "").strip()

        if not nome or not codigo or not quantidade or not valor_custo:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("parts/form.html", part=None, marcas=marcas)

        existente = Part.query.filter_by(codigo=codigo).first()
        if existente:
            flash("Já existe uma peça com esse código.", "danger")
            return render_template("parts/form.html", part=None, marcas=marcas)

        valor_custo = valor_custo.replace(",", ".")

        # Gerencia marca associada
        brand_id = None
        if marca_nome:
            brand = Brand.query.filter(func.lower(Brand.nome) == marca_nome.lower()).first()
            if not brand:
                brand = Brand(nome=marca_nome)
                db.session.add(brand)
                db.session.flush()
            brand_id = brand.id

        foto_file = request.files.get("foto_arquivo")
        foto_filename = None
        if foto_file and foto_file.filename:
            if allowed_file(foto_file.filename):
                filename = secure_filename(foto_file.filename)
                upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                foto_file.save(upload_path)
                foto_filename = filename
            else:
                flash("Formato de arquivo inválido. Envie apenas imagens (png, jpg, jpeg, gif).", "danger")
                return render_template("parts/form.html", part=None, marcas=marcas)

        part = Part(
            nome=nome,
            codigo=codigo,
            descricao=descricao,
            quantidade=int(quantidade),
            valor_custo=float(valor_custo),
            foto=foto_filename,
            brand_id=brand_id
        )
        db.session.add(part)
        db.session.commit()
        flash("Peça cadastrada com sucesso!", "success")
        return redirect(url_for("parts.list_parts"))

    return render_template("parts/form.html", part=None, marcas=marcas)


# ============================ # EDITAR PEÇA # ============================
@parts_bp.route("/editar/<int:id>", methods=["GET", "POST"])
def edit_part(id):
    part = Part.query.get_or_404(id)
    marcas = Brand.query.order_by(Brand.nome.asc()).all()

    if request.method == "POST":
        nome = request.form.get("nome", "").strip()
        codigo = request.form.get("codigo", "").strip()
        descricao = request.form.get("descricao", "").strip()
        quantidade = request.form.get("quantidade", "").strip()
        valor_custo = request.form.get("valor_custo", "").strip()
        marca_nome = request.form.get("marca", "").strip()

        if not nome or not codigo or not quantidade or not valor_custo:
            flash("Preencha todos os campos obrigatórios.", "danger")
            return render_template("parts/form.html", part=part, marcas=marcas)

        existente = Part.query.filter(Part.codigo == codigo, Part.id != part.id).first()
        if existente:
            flash("Já existe outra peça com esse código.", "danger")
            return render_template("parts/form.html", part=part, marcas=marcas)

        valor_custo = valor_custo.replace(",", ".")

        # Gerencia marca associada
        if marca_nome:
            brand = Brand.query.filter(func.lower(Brand.nome) == marca_nome.lower()).first()
            if not brand:
                brand = Brand(nome=marca_nome)
                db.session.add(brand)
                db.session.flush()
            part.brand_id = brand.id
        else:
            part.brand_id = None

        part.nome = nome
        part.codigo = codigo
        part.descricao = descricao
        part.quantidade = int(quantidade)
        part.valor_custo = float(valor_custo)

        if request.form.get("remover_foto"):
            part.foto = None

        foto_file = request.files.get("foto_arquivo")
        if foto_file and foto_file.filename:
            if allowed_file(foto_file.filename):
                filename = secure_filename(foto_file.filename)
                upload_path = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
                foto_file.save(upload_path)
                part.foto = filename
            else:
                flash("Formato de arquivo inválido. Envie apenas imagens (png, jpg, jpeg, gif).", "danger")
                return render_template("parts/form.html", part=part, marcas=marcas)

        db.session.commit()
        flash("Peça atualizada com sucesso!", "success")
        return redirect(url_for("parts.list_parts"))

    return render_template("parts/form.html", part=part, marcas=marcas)


# ============================ # EXCLUIR PEÇA # ============================
@parts_bp.route("/excluir/<int:id>")
def delete_part(id):
    part = Part.query.get_or_404(id)

    if part.movements:
        flash("Não é possível excluir peça com movimentações vinculadas.", "danger")
        return redirect(url_for("parts.list_parts"))

    db.session.delete(part)
    db.session.commit()
    flash("Peça excluída com sucesso!", "success")
    return redirect(url_for("parts.list_parts"))


# ============================ # GERAR PDF DE ETIQUETAS (FILTRÁVEL) # ============================
@parts_bp.route("/etiquetas/pdf/<modelo>")
def etiquetas_pdf(modelo):
    part_id = request.args.get("id")
    
    # Filtra por ID (única peça) ou puxa todas se o ID não for passado
    if part_id:
        parts = Part.query.filter_by(id=part_id).all()
    else:
        parts = Part.query.order_by(Part.nome.asc()).all()

    etiquetas = []

    for p in parts:
        qr_base64 = None
        barcode_base64 = None
        codigo_limpo = str(p.codigo).strip()

        if modelo in ["qrcode", "completo", "termica", "pequena", "a4"]:
            qr = qrcode.make(codigo_limpo)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()

        if modelo in ["barcode", "completo", "termica", "pequena", "a4"]:
            try:
                EAN = barcode.get_barcode_class('code128')
                ean = EAN(codigo_limpo, writer=ImageWriter())
                buffer = BytesIO()
                ean.write(buffer, options={"write_text": False})
                barcode_base64 = base64.b64encode(buffer.getvalue()).decode()
            except Exception:
                qr = qrcode.make(codigo_limpo)
                buffer = BytesIO()
                qr.save(buffer, format="PNG")
                barcode_base64 = base64.b64encode(buffer.getvalue()).decode()

        etiquetas.append({
            "codigo": p.codigo,
            "nome": p.nome,
            "marca": p.marca_nome,
            "qr": qr_base64,
            "barcode": barcode_base64
        })

    html = render_template(f"parts/etiquetas/etiquetas_{modelo}.html", etiquetas=etiquetas)
    return render_pdf_response(
        html_content=html,
        filename=f"etiquetas_{modelo}.pdf",
        fallback_endpoint="parts.list_parts"
    )


# ============================ # RELATÓRIO GERAL DE PEÇAS (PDF) # ============================
@parts_bp.route("/pdf")
def relatorio_pecas():
    filtro = request.args.get("filtro", "todas")

    query = Part.query.options(joinedload(Part.brand)).order_by(Part.nome.asc())
    if filtro == "faltando":
        query = query.filter(Part.quantidade == 0)
    elif filtro == "baixo_estoque":
        query = query.filter(Part.quantidade <= 2)

    parts = query.all()
    dia = datetime.now().strftime("%d-%m-%Y")

    html = render_template("parts/relatorio_pecas.html", pecas=parts, dia=dia, filtro=filtro)
    return render_pdf_response(
        html_content=html,
        filename=f"relatorio_pecas_{filtro}_{dia}.pdf",
        fallback_endpoint="parts.list_parts"
    )
