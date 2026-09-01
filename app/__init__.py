import os
from flask import Flask

# AJUSTE DE CAMINHOS: Usando importações relativas dentro do pacote 'app'
from .config import Config  
from .extensions import db

# Importando os Blueprints corretamente de suas respectivas pastas e arquivos routes
from .dashboard.routes import dashboard_bp
from .users.routes import users_bp
from .parts.routes import parts_bp
from .movements.routes import movements_bp  # Adicionado .routes para manter o padrão
from .backup.routes import backup_bp        # Adicionado .routes para manter o padrão
from .notes.routes import notes_bp          # <-- ADICIONADO: Import do blueprint de notas

def create_app(config_class=Config, config_override=None):
    base_dir = os.path.dirname(os.path.abspath(__file__))

    app = Flask(
        __name__,
        template_folder=os.path.join(base_dir, "templates"),
        static_folder=os.path.join(base_dir, "static")
    )

    # Carrega configurações do config.py
    app.config.from_object(config_class)
    if config_override:
        app.config.update(config_override)

    # Inicializa extensões
    db.init_app(app)

    # Garante que as tabelas e modelos estejam sempre sincronizados
    with app.app_context():
        from .models import User, Part, Brand, Movement, Note
        db.create_all()

    # Registrando blueprints
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(users_bp, url_prefix="/usuarios")
    app.register_blueprint(parts_bp, url_prefix="/pecas")
    app.register_blueprint(movements_bp, url_prefix="/movimentacoes")
    app.register_blueprint(backup_bp, url_prefix="/backup")
    app.register_blueprint(notes_bp, url_prefix="/notas")  # <-- ADICIONADO: Registro do blueprint

    # =========================================================================
    # FILTRO CUSTOMIZADO: Formatação de Moeda Brasileira (R$ 103.926,00)
    # =========================================================================
    @app.template_filter('brmoeda')
    def brmoeda_filter(valor):
        if valor is None:
            return "0,00"
        # Gera formato com milhar americana (103,926.00) e inverte os caracteres
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    return app