import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app
from app.extensions import db
from app.models import User, Part, Brand, Movement, Note

def seed_database():
    app = create_app()
    with app.app_context():
        print("[+] Iniciando o povoamento do banco de dados...")

        # 1. Marcas
        marcas_data = [
            "ALBUQUERQUE DIESEL",
            "ROBUST",
            "BOSCH",
            "GEDORE",
            "VONDER",
            "MAHLE",
            "TRAMONTINA PRO",
            "SKF",
            "SABÓ",
            "WABCO"
        ]

        marcas_map = {}
        for nome_m in marcas_data:
            brand = Brand.query.filter_by(nome=nome_m).first()
            if not brand:
                brand = Brand(nome=nome_m)
                db.session.add(brand)
                db.session.flush()
            marcas_map[nome_m] = brand

        # 2. Usuários / Colaboradores
        usuarios_data = [
            {"codigo": "USR-001", "nome": "Paulo Soares", "email": "paulo.soares@empresa.com", "telefone": "(11) 98765-4321", "funcao": "Supervisor de Manutenção"},
            {"codigo": "USR-002", "nome": "Carlos Eduardo", "email": "carlos.mecanico@empresa.com", "telefone": "(11) 97654-3210", "funcao": "Mecânico Sênior"},
            {"codigo": "USR-003", "nome": "Rafael Silva", "email": "rafael.silva@empresa.com", "telefone": "(11) 96543-2109", "funcao": "Técnico de Almoxarifado"},
            {"codigo": "USR-004", "nome": "Juliana Oliveira", "email": "juliana.oliveira@empresa.com", "telefone": "(11) 95432-1098", "funcao": "Eletricista Industrial"},
            {"codigo": "USR-005", "nome": "Marcelo Costa", "email": "marcelo.costa@empresa.com", "telefone": "(11) 94321-0987", "funcao": "Operador de Torno"},
        ]

        usuarios_map = {}
        for u_data in usuarios_data:
            user = User.query.filter_by(codigo=u_data["codigo"]).first()
            if not user:
                user = User(**u_data)
                db.session.add(user)
                db.session.flush()
            usuarios_map[u_data["codigo"]] = user

        # 3. Peças
        pecas_data = [
            {
                "codigo": "7906",
                "nome": "22 DE ENCAIXE SEXTAVADA",
                "descricao": "Chave soquete 22mm sextavada encaixe 1/2 reforçada para linha pesada",
                "quantidade": 15,
                "valor_custo": 38.50,
                "brand": marcas_map.get("ALBUQUERQUE DIESEL")
            },
            {
                "codigo": "7907",
                "nome": "24 DE ENCAIXE SEXTAVADA",
                "descricao": "Chave soquete 24mm sextavada encaixe 1/2 reforçada para linha pesada",
                "quantidade": 12,
                "valor_custo": 44.00,
                "brand": marcas_map.get("ALBUQUERQUE DIESEL")
            },
            {
                "codigo": "7025",
                "nome": "ADAPTADOR 1/2 P 1/4",
                "descricao": "Adaptador redutor de torque para soquetes manuais",
                "quantidade": 8,
                "valor_custo": 22.90,
                "brand": marcas_map.get("ROBUST")
            },
            {
                "codigo": "5010",
                "nome": "JOGO DE CHAVES COMBINADAS 6 A 22MM",
                "descricao": "Conjunto com 8 peças em aço cromo vanádio niquelado",
                "quantidade": 4,
                "valor_custo": 145.00,
                "brand": marcas_map.get("GEDORE")
            },
            {
                "codigo": "3022",
                "nome": "SENSOR DE PRESSÃO COMMON RAIL",
                "descricao": "Sensor de alta precisão para sistema de injeção diesel",
                "quantidade": 2,
                "valor_custo": 380.00,
                "brand": marcas_map.get("BOSCH")
            },
            {
                "codigo": "1005",
                "nome": "ROLAMENTO DE ESFERAS 6205-2RS",
                "descricao": "Rolamento blindado com vedação de borracha para motor elétrico",
                "quantidade": 20,
                "valor_custo": 28.50,
                "brand": marcas_map.get("SKF")
            },
            {
                "codigo": "8040",
                "nome": "DISCO DE CORTE FINO 4.1/2 X 1.0MM",
                "descricao": "Disco abrasivo para corte rápido de aço inox e carbono",
                "quantidade": 50,
                "valor_custo": 5.80,
                "brand": marcas_map.get("VONDER")
            },
            {
                "codigo": "6015",
                "nome": "RETENTOR DO VIRABREQUIM DIANTEIRO",
                "descricao": "Retentor em poliacrílico de vedação do eixo virabrequim",
                "quantidade": 0,
                "valor_custo": 62.00,
                "brand": marcas_map.get("SABÓ")
            },
            {
                "codigo": "4012",
                "nome": "KIT JUNTAS SUPERIOR DO MOTOR",
                "descricao": "Jogo de juntas e vedadores metálicos para cabeçote",
                "quantidade": 1,
                "valor_custo": 290.00,
                "brand": marcas_map.get("MAHLE")
            },
            {
                "codigo": "2001",
                "nome": "PARAFUSO SEXTAVADO M10 X 40MM",
                "descricao": "Parafuso zincado rosca métrica inteira grau 8.8",
                "quantidade": 150,
                "valor_custo": 1.50,
                "brand": None
            },
            {
                "codigo": "9011",
                "nome": "VÁLVULA DE FREIO DE ESTACIONAMENTO",
                "descricao": "Válvula pneumática moduladora de freio a ar",
                "quantidade": 3,
                "valor_custo": 410.00,
                "brand": marcas_map.get("WABCO")
            },
            {
                "codigo": "5020",
                "nome": "ALICATE UNIVERSAL ISOLADO 1000V 8 POL",
                "descricao": "Alicate isolado para manutenção elétrica industrial",
                "quantidade": 6,
                "valor_custo": 78.00,
                "brand": marcas_map.get("TRAMONTINA PRO")
            }
        ]

        pecas_map = {}
        for p_data in pecas_data:
            part = Part.query.filter_by(codigo=p_data["codigo"]).first()
            if not part:
                part = Part(**p_data)
                db.session.add(part)
                db.session.flush()
            pecas_map[p_data["codigo"]] = part

        # 4. Movimentações
        agora = datetime.now()
        movimentacoes_data = [
            {
                "tipo": "saida",
                "user": usuarios_map["USR-002"],
                "part": pecas_map["7906"],
                "quantidade": 1,
                "data_hora": agora - timedelta(hours=2),
                "emprestimo_aberto": True,
                "observacao": "Retirada para montagem do eixo traseiro no box 3"
            },
            {
                "tipo": "saida",
                "user": usuarios_map["USR-004"],
                "part": pecas_map["5020"],
                "quantidade": 1,
                "data_hora": agora - timedelta(hours=4),
                "emprestimo_aberto": True,
                "observacao": "Manutenção no quadro de distribuição da oficina"
            },
            {
                "tipo": "saida",
                "user": usuarios_map["USR-005"],
                "part": pecas_map["7025"],
                "quantidade": 1,
                "data_hora": agora - timedelta(days=1, hours=3),
                "emprestimo_aberto": False,
                "data_devolucao": agora - timedelta(days=1, hours=1),
                "devolvido_por": "Marcelo Costa",
                "observacao": "Utilizado para ajuste de torque. Devolvido limpo."
            },
            {
                "tipo": "saida",
                "user": usuarios_map["USR-003"],
                "part": pecas_map["8040"],
                "quantidade": 5,
                "data_hora": agora - timedelta(days=2),
                "emprestimo_aberto": False,
                "data_devolucao": agora - timedelta(days=2) + timedelta(minutes=45),
                "devolvido_por": "Rafael Silva",
                "observacao": "Corte de perfis para bancada auxiliar."
            },
            {
                "tipo": "saida",
                "user": usuarios_map["USR-002"],
                "part": pecas_map["1005"],
                "quantidade": 2,
                "data_hora": agora - timedelta(days=3),
                "emprestimo_aberto": False,
                "data_devolucao": agora - timedelta(days=3, hours=-2),
                "devolvido_por": "Carlos Eduardo",
                "observacao": "Substituição preventiva no motor da bomba d'água."
            }
        ]

        for m_data in movimentacoes_data:
            # Evita duplicar se já existir exatamente a mesma movimentação
            existente = Movement.query.filter_by(
                user_id=m_data["user"].id,
                part_id=m_data["part"].id,
                data_hora=m_data["data_hora"]
            ).first()
            if not existente:
                mov = Movement(**m_data)
                db.session.add(mov)

        # 5. Notas Internas
        notas_data = [
            {
                "titulo": "Inventário Geral do Almoxarifado",
                "conteudo": "Agendada contagem física das prateleiras A, B e C para o final do mês. Conferir saldo de soquetes e retentores.",
                "user": usuarios_map["USR-001"],
                "data_criacao": agora - timedelta(days=2)
            },
            {
                "titulo": "Aviso de Peças em Falta",
                "conteudo": "Retentor do virabrequim (cód 6015) está esgotado. Solicitar cotação urgente com distribuidor SABÓ.",
                "user": usuarios_map["USR-003"],
                "data_criacao": agora - timedelta(days=1)
            },
            {
                "titulo": "Normas de Empréstimo de Ferramentas",
                "conteudo": "Lembrar todos os operadores de registrar a devolução com data/hora e conferir a integridade visual das peças.",
                "user": usuarios_map["USR-001"],
                "data_criacao": agora
            }
        ]

        for n_data in notas_data:
            existente = Note.query.filter_by(titulo=n_data["titulo"]).first()
            if not existente:
                nota = Note(**n_data)
                db.session.add(nota)

        db.session.commit()
        print("[OK] Banco de dados populado com sucesso!")
        print(f"   * {Brand.query.count()} Marcas")
        print(f"   * {User.query.count()} Usuarios")
        print(f"   * {Part.query.count()} Pecas")
        print(f"   * {Movement.query.count()} Movimentacoes")
        print(f"   * {Note.query.count()} Notas")

if __name__ == "__main__":
    seed_database()
