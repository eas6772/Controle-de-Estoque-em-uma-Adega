from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models import Product
from app.services.inventory import register_sale


vendas_bp = Blueprint("vendas", __name__)


@vendas_bp.route("/pdv", methods=["GET", "POST"])
@login_required
def pdv():
    if request.method == "POST":
        codigo_barras = request.form.get("codigo_barras")
        quantidade = int(request.form.get("quantidade", 1))
        produto = Product.query.filter_by(codigo_barras=codigo_barras).first()
        if not produto:
            flash("Produto não encontrado.", "warning")
            return redirect(url_for("vendas.pdv"))
        try:
            register_sale(produto, quantidade, current_user.id)
            flash("Venda registrada com sucesso pelo método PEPS.", "success")
        except ValueError as error:
            flash(str(error), "danger")
        return redirect(url_for("vendas.pdv"))
    return render_template("vendas/pdv.html")
