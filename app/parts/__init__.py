from flask import Blueprint

parts_bp = Blueprint("parts", __name__, template_folder="../../templates/parts")

from . import routes 
