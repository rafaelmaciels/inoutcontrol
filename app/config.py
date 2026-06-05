import os

# Caminho absoluto da pasta onde este arquivo está (InOutControl/app)
APP_DIR = os.path.abspath(os.path.dirname(__file__))

# Caminho da raiz do projeto (InOutControl), subindo um nível
BASE_DIR = os.path.abspath(os.path.join(APP_DIR, os.parentdir if hasattr(os, 'parentdir') else '..'))

class Config:
    # Chave secreta para sessões e CSRF
    SECRET_KEY = os.environ.get("SECRET_KEY", "troque-esta-chave")

    # Torna o BASE_DIR acessível via current_app.config["BASE_DIR"]
    BASE_DIR = BASE_DIR

    # Caminho do banco de dados SQLite - Apontando para a RAIZ do projeto
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, 'inoutcontrol.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Upload de imagens das peças (agora centralizado no BASE_DIR da raiz ou APP_DIR se preferir na pasta app)
    UPLOAD_FOLDER = os.path.join(APP_DIR, "static", "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

    # Config extra para migrations
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True
    }
