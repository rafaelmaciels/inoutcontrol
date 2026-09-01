import sqlite3
import re
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models import Part, Brand

KNOWN_BRANDS = [
    "ALBUQUERQUE DIESEL",
    "ROBUST",
    "BOSCH",
    "GEDORE",
    "VONDER",
    "MAHLE",
    "TRAMONTINA",
    "SATA",
    "BELZER",
    "3M",
    "SKF",
    "TIMKEN",
    "SABÓ",
    "SABO",
    "WABCO",
    "KNORR",
    "DELPHI",
    "MAGNETI MARELLI",
    "DAYCO",
    "GATES",
    "VALEO",
    "NGK",
    "DENSO",
    "COFAP",
    "MONROE",
    "NAKATA",
    "FRAS-LE",
    "LONAFLEX",
    "VARGA",
    "TRW"
]

def analyze_parts(app=None):
    if app is None:
        app = create_app()
    results = []

    with app.app_context():
        # Garante tabelas criadas
        db.create_all()
        parts = Part.query.order_by(Part.id.asc()).all()

        for p in parts:
            descricao_str = (p.descricao or "").upper()
            nome_str = (p.nome or "").upper()

            detected_brand = None
            confidence = "BAIXA"
            reason = "Sem marca identificada"

            # 1. Verifica se já possui marca associada no modelo
            if p.brand:
                detected_brand = p.brand.nome
                confidence = "ALTA"
                reason = "Marca já associada no cadastro da peça"

            # 2. Procura marcas conhecidas na descrição
            if not detected_brand:
                for brand in KNOWN_BRANDS:
                    pattern = r'\b' + re.escape(brand) + r'\b'
                    if re.search(pattern, descricao_str):
                        detected_brand = brand
                        confidence = "ALTA"
                        reason = f"Informação encontrada na descrição: '{p.descricao}'"
                        break

            # 3. Procura marcas conhecidas no nome
            if not detected_brand:
                for brand in KNOWN_BRANDS:
                    pattern = r'\b' + re.escape(brand) + r'\b'
                    if re.search(pattern, nome_str):
                        detected_brand = brand
                        confidence = "ALTA"
                        reason = f"Informação encontrada no nome: '{p.nome}'"
                        break

            # 4. Padrão explícito 'MARCA: XXX'
            if not detected_brand:
                match = re.search(r'(?:MARCA|FABRICANTE)\s*[:\-]\s*([A-Z0-9\s\-]+)', descricao_str)
                if match:
                    detected_brand = match.group(1).strip()
                    confidence = "ALTA"
                    reason = "Padrão explícito 'MARCA/FABRICANTE' na descrição"

            if not detected_brand:
                detected_brand = "Não identificada"
                confidence = "N/A"
                reason = "Nenhuma menção explícita de marca encontrada"

            results.append({
                "id": p.id,
                "codigo": p.codigo,
                "nome": p.nome,
                "marca": detected_brand,
                "confianca": confidence,
                "motivo": reason
            })

    return results

if __name__ == "__main__":
    analysis = analyze_parts()
    print(f"Total de peças analisadas: {len(analysis)}")
    print("PEÇA | CÓDIGO | MARCA IDENTIFICADA | CONFIANÇA | MOTIVO")
    print("-" * 75)
    for item in analysis:
        print(f"{item['id']} | {item['codigo']} | {item['nome']} | {item['marca']} | {item['confianca']} | {item['motivo']}")
