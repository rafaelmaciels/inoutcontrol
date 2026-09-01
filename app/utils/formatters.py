from datetime import datetime
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif"}

def allowed_file(filename: str) -> bool:
    """Valida se a extensão do arquivo enviado é uma imagem permitida."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def parse_date(date_str: str):
    """Realiza o parse de strings de data suportando os formatos DD-MM-YYYY e YYYY-MM-DD."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%d-%m-%Y")
    except ValueError:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return None

def tempo_relativo(dt: datetime) -> str:
    """Calcula uma descrição textual amigável do tempo decorrido."""
    if not dt:
        return ""
    agora = datetime.now()
    diff = agora - dt
    segundos = diff.total_seconds()
    if segundos < 60:
        return "agora mesmo"
    elif segundos < 3600:
        return f"há {int(segundos // 60)} min"
    elif segundos < 86400:
        return f"há {int(segundos // 3600)} h"
    else:
        return f"há {int(segundos // 86400)} dias"

def formatar_moeda_br(valor) -> str:
    """Formata valor numérico para o padrão de moeda brasileira (R$ 1.234,56)."""
    if valor is None:
        return "0,00"
    return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def padronizar_codigo(codigo: str) -> str:
    """Padroniza códigos de peças/itens e usuários removendo espaços extras e convertendo para maiúsculas."""
    if not codigo:
        return ""
    return str(codigo).strip().upper()

def gerar_proximo_codigo_peca() -> str:
    """
    Analisa os códigos existentes no banco de dados e gera automaticamente o próximo
    código numérico sequencial padronizado de 4 dígitos (ou superior), evitando 100% de duplicidades.
    Exemplo: Se o maior código existente for '9011', gera '9012'.
    Caso não existam códigos numéricos, inicia em '1001'.
    """
    from app.models import Part

    codigos = [p.codigo for p in Part.query.with_entities(Part.codigo).all() if p.codigo]

    numericos = []
    for c in codigos:
        c_clean = str(c).strip()
        if c_clean.isdigit():
            numericos.append(int(c_clean))

    if numericos:
        proximo_num = max(numericos) + 1
    else:
        proximo_num = 1001

    proximo_codigo = f"{proximo_num:04d}"

    while Part.query.filter_by(codigo=proximo_codigo).first() is not None:
        proximo_num += 1
        proximo_codigo = f"{proximo_num:04d}"

    return proximo_codigo

