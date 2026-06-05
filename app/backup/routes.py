from flask import render_template, request, send_file, flash, redirect, url_for, current_app
from . import backup_bp
import os
import datetime
import zipfile
import sqlite3
import pyminizip


# Página do formulário
@backup_bp.route("/")
def backup_form():
    return render_template("backup/form.html")


# Exportar backup (ZIP com senha)
@backup_bp.route("/exportar", methods=["POST"])
def backup_execute():

    nome = request.form.get("nome")
    senha = request.form.get("senha")

    if not senha:
        flash("Digite uma senha para proteger o backup.", "danger")
        return redirect(url_for("backup.backup_form"))

    # Caminho do banco
    db_path = os.path.join(current_app.config["BASE_DIR"], "stockcontrol.db")

    if not os.path.exists(db_path):
        flash("Banco de dados não encontrado!", "danger")
        return redirect(url_for("backup.backup_form"))

    # Data no formato solicitado
    data = datetime.datetime.now().strftime("%d-%m-%Y")

    # Nome final do ZIP
    zip_name = f"{nome}_{data}.zip"
    zip_path = os.path.join(current_app.config["BASE_DIR"], zip_name)

    # Cria ZIP com senha
    pyminizip.compress(
        db_path,      # arquivo de entrada
        None,         # sem pasta raiz
        zip_path,     # arquivo de saída
        senha,        # senha digitada
        5             # nível de compressão (1–9)
    )

    return send_file(
        zip_path,
        as_attachment=True,
        download_name=zip_name
    )


# Função para validar se o arquivo extraído é SQLite
def is_valid_sqlite(file_path):
    try:
        conn = sqlite3.connect(file_path)
        conn.execute("PRAGMA schema_version;")
        conn.close()
        return True
    except:
        return False


# Importar backup (ZIP com senha)
@backup_bp.route("/importar", methods=["POST"])
def backup_import():

    senha = request.form.get("senha")
    arquivo = request.files.get("arquivo")

    if not arquivo or not arquivo.filename.endswith(".zip"):
        flash("Selecione um arquivo ZIP válido.", "danger")
        return redirect(url_for("backup.backup_form"))

    if not senha:
        flash("Digite a senha do backup.", "danger")
        return redirect(url_for("backup.backup_form"))

    # Caminhos temporários
    temp_zip = os.path.join(current_app.config["BASE_DIR"], "temp_backup.zip")
    temp_db = os.path.join(current_app.config["BASE_DIR"], "stockcontrol.db")  # <-- CORRIGIDO

    # Salva o ZIP temporário
    arquivo.save(temp_zip)

    # Tenta extrair o ZIP com a senha
    try:
        with zipfile.ZipFile(temp_zip) as z:
            z.extractall(
                path=current_app.config["BASE_DIR"],
                pwd=senha.encode()
            )
    except:
        os.remove(temp_zip)
        flash("Senha incorreta ou arquivo ZIP inválido!", "danger")
        return redirect(url_for("backup.backup_form"))

    # Verifica se o arquivo extraído é SQLite
    if not os.path.exists(temp_db) or not is_valid_sqlite(temp_db):
        if os.path.exists(temp_db):
            os.remove(temp_db)
        os.remove(temp_zip)
        flash("O ZIP não contém um banco SQLite válido.", "danger")
        return redirect(url_for("backup.backup_form"))

    # Caminho do banco atual
    db_path = os.path.join(current_app.config["BASE_DIR"], "stockcontrol.db")

    # Substitui o banco atual
    os.replace(temp_db, db_path)

    # Remove o ZIP temporário
    os.remove(temp_zip)

    flash("Backup importado com sucesso! Reinicie o servidor.", "success")
    return redirect(url_for("backup.backup_form"))
