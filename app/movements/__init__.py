from flask import Blueprint

movements_bp = Blueprint(
    "movements",
    __name__,
    url_prefix="/movimentacoes",
    template_folder="../../templates/movements"
)

# IMPORT ABSOLUTO — ESSENCIAL
from . import routes
