from flask import Blueprint, render_template
from flask_login import login_required

from app.models import Product, StockMovement


admin_bp = Blueprint("admin", __name__)


@admin_bp.route("/")
@login_required
def index():
    total_produtos = Product.query.count()
    total_movimentacoes = StockMovement.query.count()
    return render_template(
        "admin/index.html",
        total_produtos=total_produtos,
        total_movimentacoes=total_movimentacoes,
    )
