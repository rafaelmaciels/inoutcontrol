import os
from flask import send_from_directory, flash, redirect, request

# AJUSTE DE CAMINHOS: Agora importamos de dentro do pacote 'app'
from app import create_app
from app.extensions import db
from app.models import User, Part, Movement, Note, Brand
from app.utils.db_migrations import run_migrations

# ============================ # CRIAÇÃO DO APP # ============================
app = create_app()

# Executa criação e migrações automáticas de banco de dados
with app.app_context():
    db.create_all()
    db_file = os.path.join(app.config["BASE_DIR"], "inoutcontrol.db")
    run_migrations(db_file)

# Define limite máximo de upload (exemplo: 5 MB)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

# Define pasta de uploads dentro de static
app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "static", "uploads")

# Garante que a pasta de uploads exista
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)


# ============================ # TRATAMENTO DE ERRO 413 # ============================
@app.errorhandler(413)
def too_large(e):
    """
    Tratamento para uploads maiores que o limite definido.
    Retorna mensagem amigável ao usuário em vez da tela padrão.
    """
    flash("Arquivo muito grande. O limite é de 5 MB.", "danger")
    return redirect(request.url)


# ============================ # MAIN # ============================
if __name__ == "__main__":
    # Cria as tabelas no banco de dados se não existirem
    with app.app_context():
        db.create_all()
    # Executa o servidor em modo debug
    app.run(debug=True)
