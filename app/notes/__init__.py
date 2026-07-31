from flask import Blueprint

notes_bp = Blueprint("notes", __name__, template_folder="../../templates/notes")

from . import routes