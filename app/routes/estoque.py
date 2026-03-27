from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Batch, Product, StockMovement


estoque_bp = Blueprint("estoque", __name__)


@estoque_bp.route("/")
@login_required
def listar():
    categoria = request.args.get("categoria")
    query = Product.query
    if categoria:
        query = query.join(Product.categoria).filter_by(nome=categoria)
    produtos = query.all()
    return render_template("estoque/listar.html", produtos=produtos)


@estoque_bp.route("/entrada-rapida/<int:produto_id>", methods=["POST"])
@login_required
def entrada_rapida(produto_id: int):
    produto = Product.query.get_or_404(produto_id)
    data_validade_str = request.form.get("data_validade")
    if not data_validade_str:
        flash("Informe a data de validade do lote.", "warning")
        return redirect(url_for("estoque.listar"))
    data_validade = datetime.strptime(data_validade_str, "%Y-%m-%d").date()
    lote = Batch(
        produto_id=produto.id,
        quantidade=int(request.form.get("quantidade", 0)),
        data_validade=data_validade,
    )
    db.session.add(lote)
    db.session.add(
        StockMovement(
            produto_id=produto.id,
            tipo="entrada",
            quantidade=lote.quantidade,
            usuario_id=current_user.id,
            motivo="Entrada rápida",
        )
    )
    db.session.commit()
    flash("Entrada rápida registrada.", "success")
    return redirect(url_for("estoque.listar"))
