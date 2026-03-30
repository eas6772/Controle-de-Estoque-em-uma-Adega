from datetime import datetime, date
from decimal import Decimal

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from .extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id: str):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="operador")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    movements = db.relationship("StockMovement", back_populates="usuario")

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40), unique=True, nullable=False)
    margem_de_lucro = db.Column(db.Numeric(8, 2), nullable=False, default=Decimal("1.10"))

    produtos = db.relationship("Product", back_populates="categoria")


class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(120), nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey("category.id"), nullable=False)
    marca = db.Column(db.String(80), nullable=False)
    codigo_barras = db.Column(db.String(30), unique=True, nullable=True)
    preco_custo = db.Column(db.Numeric(10, 2), nullable=False)
    preco_venda = db.Column(db.Numeric(10, 2), nullable=False)
    estoque_min = db.Column(db.Integer, nullable=False, default=0)
    estoque_max = db.Column(db.Integer, nullable=False, default=0)
    teor_alcoolico = db.Column(db.Float)
    volume_ml = db.Column(db.Integer)
    tipo_tabacaria = db.Column(db.String(50))
    peso_g = db.Column(db.Integer)
    sabor = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    categoria = db.relationship("Category", back_populates="produtos")
    lotes = db.relationship("Batch", back_populates="produto", cascade="all, delete-orphan")
    movimentacoes = db.relationship("StockMovement", back_populates="produto")

    @property
    def estoque_total(self) -> int:
        return sum(lote.quantidade for lote in self.lotes)

    @property
    def estoque_baixo(self) -> bool:
        return self.estoque_total <= self.estoque_min

    def validar_preco(self) -> None:
        if Decimal(self.preco_venda) <= Decimal(self.preco_custo):
            raise ValueError("Preço de venda deve ser maior que preço de custo.")


class Batch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False, default=0)
    data_validade = db.Column(db.Date, nullable=False)
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    produto = db.relationship("Product", back_populates="lotes")

    @property
    def expirado(self) -> bool:
        return self.data_validade < date.today()


class StockMovement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    produto_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)
    quantidade = db.Column(db.Integer, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    data_hora = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    motivo = db.Column(db.String(255))

    produto = db.relationship("Product", back_populates="movimentacoes")
    usuario = db.relationship("User", back_populates="movements")
