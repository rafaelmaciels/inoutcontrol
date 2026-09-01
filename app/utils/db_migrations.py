import sqlite3
import os

def run_migrations(db_path: str):
    """
    Executa migrações incrementais e seguras no banco de dados SQLite.
    Garante idempotência e retrocompatibilidade com dados legados existentes.
    """
    if not os.path.exists(db_path):
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    try:
        # 1. Cria a tabela brands se não existir
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS brands (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome VARCHAR(100) NOT NULL UNIQUE,
                data_criacao DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # 2. Cria índice no nome da marca se não existir
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_brands_nome ON brands(nome)")

        # 3. Verifica se a tabela parts existe
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='parts'")
        parts_exists = cursor.fetchone()

        if parts_exists:
            # Verifica se a coluna brand_id já existe na tabela parts
            cursor.execute("PRAGMA table_info(parts)")
            columns = [row[1] for row in cursor.fetchall()]

            if "brand_id" not in columns:
                cursor.execute("ALTER TABLE parts ADD COLUMN brand_id INTEGER REFERENCES brands(id)")

            cursor.execute("CREATE INDEX IF NOT EXISTS ix_parts_brand_id ON parts(brand_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_parts_codigo ON parts(codigo)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_parts_nome ON parts(nome)")

        # 4. Verifica se a tabela movements existe para criar índices
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='movements'")
        movements_exists = cursor.fetchone()
        if movements_exists:
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_movements_data_hora ON movements(data_hora)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_movements_emprestimo_aberto ON movements(emprestimo_aberto)")

        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()
