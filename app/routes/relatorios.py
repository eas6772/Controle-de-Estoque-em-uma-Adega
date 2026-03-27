from flask import Blueprint, render_template

from app.models import StockMovement


relatorios_bp = Blueprint("relatorios", __name__)


@relatorios_bp.route("/")
def index():
    movimentacoes = (
        StockMovement.query.order_by(StockMovement.data_hora.desc()).limit(50).all()
    )
    return render_template("relatorios/index.html", movimentacoes=movimentacoes)
