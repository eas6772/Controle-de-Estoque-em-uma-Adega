from flask import Blueprint, render_template

from app.models import Batch, Product, StockMovement


main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def dashboard():
    total_estoque = sum(produto.estoque_total for produto in Product.query.all())
    alertas_validade = Batch.query.filter(Batch.quantidade > 0).count()
    vendas_hoje = StockMovement.query.filter_by(tipo="venda").count()
    return render_template(
        "dashboard.html",
        total_estoque=total_estoque,
        alertas_validade=alertas_validade,
        vendas_hoje=vendas_hoje,
    )
