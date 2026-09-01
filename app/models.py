from datetime import datetime
from sqlalchemy.orm import validates
# AJUSTE DE CAMINHO: Importando a extensão usando o ponto relativo do pacote 'app'
from .extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True)
    nome = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=False)
    funcao = db.Column(db.String(100), nullable=False)

    movements = db.relationship("Movement", back_populates="user")
    notes = db.relationship("Note", back_populates="user")  # Relacionamento com as notas

    @validates('codigo')
    def validate_codigo(self, key, value):
        if value is not None:
            return str(value).strip().upper()
        return value

    def __repr__(self):
        return f"<User {self.codigo} - {self.nome}>"

class Brand(db.Model):
    __tablename__ = "brands"

    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True, index=True)
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    parts = db.relationship("Part", back_populates="brand")

    def __repr__(self):
        return f"<Brand {self.nome}>"

class Part(db.Model):
    __tablename__ = "parts"

    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nome = db.Column(db.String(120), nullable=False, index=True)
    descricao = db.Column(db.Text, nullable=True)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    foto = db.Column(db.String(255), nullable=True)
    valor_custo = db.Column(db.Float, nullable=False, default=0.0)

    # Relacionamento com Marca
    brand_id = db.Column(db.Integer, db.ForeignKey("brands.id"), nullable=True, index=True)
    brand = db.relationship("Brand", back_populates="parts")

    movements = db.relationship("Movement", back_populates="part")

    @validates('nome')
    def validate_nome(self, key, value):
        if value is not None:
            return str(value).strip().upper()
        return value

    @validates('codigo')
    def validate_codigo(self, key, value):
        if value is not None:
            return str(value).strip().upper()
        return value

    @property
    def marca_nome(self):
        return self.brand.nome if self.brand else ""

    def __repr__(self):
        return f"<Part {self.codigo} - {self.nome}>"

class Movement(db.Model):
    __tablename__ = "movements"

    id = db.Column(db.Integer, primary_key=True)
    tipo = db.Column(db.String(20), nullable=False, index=True)  # 'saida' ou 'entrada'

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    part_id = db.Column(db.Integer, db.ForeignKey("parts.id"), nullable=False, index=True)

    quantidade = db.Column(db.Integer, nullable=False, default=1)
    
    # Mantido datetime.now conforme sua ótima correção local
    data_hora = db.Column(db.DateTime, default=datetime.now, index=True)

    emprestimo_aberto = db.Column(db.Boolean, default=True, index=True)
    data_devolucao = db.Column(db.DateTime, nullable=True)
    observacao = db.Column(db.Text, nullable=True)
    devolvido_por = db.Column(db.String(120), nullable=True)

    user = db.relationship("User", back_populates="movements")
    part = db.relationship("Part", back_populates="movements")

    def __repr__(self):
        return f"<Movement {self.tipo} - {self.part.nome}>"

# ============================ # NOVO MODELO DE NOTAS # ============================
class Note(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(120), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.now)

    # Relacionamento opcional com o Usuário que criou a anotação
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    user = db.relationship("User", back_populates="notes")

    def __repr__(self):
        return f"<Note {self.titulo}>"