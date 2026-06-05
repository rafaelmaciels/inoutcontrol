from flask import Blueprint

backup_bp = Blueprint(
    "backup",
    __name__,
    template_folder="../templates"  # aponta para a pasta templates raiz
)

from . import routes
