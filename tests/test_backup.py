import os
from app.extensions import db
from app.models import User, Part

def test_backup_form_access(client):
    res = client.get("/backup/")
    assert res.status_code == 200
    assert b"Exportar Backup" in res.data or b"Importar Backup" in res.data or b"backup" in res.data.lower()
