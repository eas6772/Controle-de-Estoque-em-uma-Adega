from datetime import datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Batch, Category, Product, StockMovement


estoque_bp = Blueprint("estoque", __name__)


def _redirect_listar():
    cat = (request.form.get("retorno_categoria") or "").strip()
    return redirect(url_for("estoque.listar", **({"categoria": cat} if cat else {})))


def _optional_int(name: str) -> int | None:
    raw = request.form.get(name)
    if raw is None or str(raw).strip() == "":
        return None
    return int(raw)


def _optional_float(name: str) -> float | None:
    raw = request.form.get(name)
    if raw is None or str(raw).strip() == "":
        return None
    return float(raw)


def _preencher_produto_do_form(produto: Product) -> str | None:
    nome = (request.form.get("nome") or "").strip()
    marca = (request.form.get("marca") or "").strip()
    codigo_barras = (request.form.get("codigo_barras") or "").strip()
    if not nome or not marca:
        return "Nome e marca são obrigatórios."

    cid_raw = request.form.get("categoria_id")
    if not cid_raw:
        return "Selecione uma categoria."
    categoria = Category.query.get(int(cid_raw))
    if not categoria:
        return "Categoria inválida."

    try:
        preco_custo = Decimal(str(request.form.get("preco_custo", "")).replace(",", "."))
        preco_venda = Decimal(str(request.form.get("preco_venda", "")).replace(",", "."))
    except (InvalidOperation, TypeError):
        return "Preços inválidos."

    try:
        estoque_min = int(request.form.get("estoque_min") or 0)
        estoque_max = int(request.form.get("estoque_max") or 0)
    except ValueError:
        return "Estoque mínimo ou máximo inválido."

    produto.nome = nome
    produto.marca = marca
    produto.codigo_barras = codigo_barras or None
    produto.categoria_id = categoria.id
    produto.preco_custo = preco_custo
    produto.preco_venda = preco_venda
    produto.estoque_min = estoque_min
    produto.estoque_max = estoque_max

    try:
        produto.teor_alcoolico = _optional_float("teor_alcoolico")
        produto.volume_ml = _optional_int("volume_ml")
        produto.tipo_tabacaria = (request.form.get("tipo_tabacaria") or "").strip() or None
        produto.peso_g = _optional_int("peso_g")
        produto.sabor = (request.form.get("sabor") or "").strip() or None
    except ValueError:
        return "Campos numéricos opcionais inválidos."

    try:
        produto.validar_preco()
    except ValueError as exc:
        return str(exc)

    return None


@estoque_bp.route("/categoria/criar", methods=["POST"])
@login_required
def categoria_criar():
    nome = (request.form.get("nome") or "").strip()
    if not nome:
        flash("Informe o nome da categoria.", "warning")
        return _redirect_listar()
    if len(nome) > 40:
        flash("Nome da categoria muito longo (máx. 40 caracteres).", "warning")
        return _redirect_listar()
    if Category.query.filter_by(nome=nome).first():
        flash("Já existe uma categoria com esse nome.", "warning")
        return _redirect_listar()
    db.session.add(Category(nome=nome))
    db.session.commit()
    flash("Categoria criada.", "success")
    return _redirect_listar()


@estoque_bp.route("/categoria/<int:categoria_id>/editar", methods=["POST"])
@login_required
def categoria_editar(categoria_id: int):
    cat = Category.query.get_or_404(categoria_id)
    old_nome = cat.nome
    nome = (request.form.get("nome") or "").strip()
    if not nome:
        flash("Nome da categoria não pode ficar vazio.", "warning")
        return _redirect_listar()
    if len(nome) > 40:
        flash("Nome da categoria muito longo (máx. 40 caracteres).", "warning")
        return _redirect_listar()
    if Category.query.filter(Category.nome == nome, Category.id != cat.id).first():
        flash("Já existe outra categoria com esse nome.", "warning")
        return _redirect_listar()
    cat.nome = nome
    db.session.commit()
    flash("Categoria atualizada.", "success")
    retorno = (request.form.get("retorno_categoria") or "").strip()
    if retorno == old_nome:
        retorno = nome
    return redirect(url_for("estoque.listar", **({"categoria": retorno} if retorno else {})))


@estoque_bp.route("/categoria/<int:categoria_id>/excluir", methods=["POST"])
@login_required
def categoria_excluir(categoria_id: int):
    cat = Category.query.get_or_404(categoria_id)
    if Product.query.filter_by(categoria_id=cat.id).first():
        flash("Não é possível excluir: existem produtos nesta categoria.", "warning")
        return _redirect_listar()
    retorno = (request.form.get("retorno_categoria") or "").strip()
    if retorno == cat.nome:
        retorno = ""
    db.session.delete(cat)
    db.session.commit()
    flash("Categoria excluída.", "success")
    return redirect(url_for("estoque.listar", **({"categoria": retorno} if retorno else {})))


@estoque_bp.route("/")
@login_required
def listar():
    categoria = request.args.get("categoria")
    query = Product.query
    if categoria:
        query = query.join(Product.categoria).filter_by(nome=categoria)
    produtos = query.order_by(Product.nome).all()
    categorias = Category.query.order_by(Category.nome).all()
    return render_template(
        "estoque/listar.html",
        produtos=produtos,
        categorias=categorias,
        filtro_categoria=categoria or "",
    )


@estoque_bp.route("/produto/criar", methods=["POST"])
@login_required
def produto_criar():
    if not Category.query.count():
        flash("Cadastre categorias antes de incluir produtos.", "warning")
        return _redirect_listar()
    produto = Product()
    erro = _preencher_produto_do_form(produto)
    if erro:
        flash(erro, "danger")
        return _redirect_listar()
    if produto.codigo_barras and Product.query.filter_by(codigo_barras=produto.codigo_barras).first():
        flash("Já existe produto com este código de barras.", "warning")
        return _redirect_listar()

    try:
        qty_inicial = int(request.form.get("quantidade_inicial") or 0)
    except ValueError:
        flash("Quantidade inicial inválida.", "warning")
        return _redirect_listar()
    if qty_inicial < 0:
        flash("Quantidade inicial não pode ser negativa.", "warning")
        return _redirect_listar()

    data_validade_str = (request.form.get("data_validade") or "").strip()
    if qty_inicial > 0 and not data_validade_str:
        flash("Informe a data de validade do lote quando houver quantidade inicial.", "warning")
        return _redirect_listar()
    data_validade = None
    if data_validade_str:
        try:
            data_validade = datetime.strptime(data_validade_str, "%Y-%m-%d").date()
        except ValueError:
            flash("Data de validade inválida.", "warning")
            return _redirect_listar()

    db.session.add(produto)
    db.session.flush()
    if qty_inicial > 0 and data_validade is not None:
        agora = datetime.utcnow()
        db.session.add(
            Batch(
                produto_id=produto.id,
                quantidade=qty_inicial,
                data_validade=data_validade,
                data_entrada=agora,
            )
        )
        db.session.add(
            StockMovement(
                produto_id=produto.id,
                tipo="entrada",
                quantidade=qty_inicial,
                usuario_id=current_user.id,
                motivo="Cadastro de produto",
            )
        )
    db.session.commit()
    flash("Produto cadastrado.", "success")
    return _redirect_listar()


@estoque_bp.route("/produto/<int:produto_id>/editar", methods=["POST"])
@login_required
def produto_editar(produto_id: int):
    produto = Product.query.get_or_404(produto_id)
    erro = _preencher_produto_do_form(produto)
    if erro:
        flash(erro, "danger")
        return _redirect_listar()
    duplicado = None
    if produto.codigo_barras:
        duplicado = Product.query.filter(
            Product.codigo_barras == produto.codigo_barras, Product.id != produto.id
        ).first()
    if duplicado:
        flash("Já existe outro produto com este código de barras.", "warning")
        return _redirect_listar()
    db.session.commit()
    flash("Produto atualizado.", "success")
    return _redirect_listar()


@estoque_bp.route("/produto/<int:produto_id>/excluir", methods=["POST"])
@login_required
def produto_excluir(produto_id: int):
    produto = Product.query.get_or_404(produto_id)
    StockMovement.query.filter_by(produto_id=produto.id).delete()
    Batch.query.filter_by(produto_id=produto.id).delete()
    db.session.delete(produto)
    db.session.commit()
    flash("Produto excluído.", "success")
    return _redirect_listar()


@estoque_bp.route("/entrada-rapida/<int:produto_id>", methods=["POST"])
@login_required
def entrada_rapida(produto_id: int):
    produto = Product.query.get_or_404(produto_id)
    data_validade_str = request.form.get("data_validade")
    if not data_validade_str:
        flash("Informe a data de validade do lote.", "warning")
        return _redirect_listar()
    data_validade = datetime.strptime(data_validade_str, "%Y-%m-%d").date()
    try:
        qtd = int(request.form.get("quantidade", 0))
    except ValueError:
        flash("Quantidade inválida.", "warning")
        return _redirect_listar()
    if qtd < 1:
        flash("Informe uma quantidade maior ou igual a 1.", "warning")
        return _redirect_listar()
    agora = datetime.utcnow()
    lote = Batch(
        produto_id=produto.id,
        quantidade=qtd,
        data_validade=data_validade,
        data_entrada=agora,
    )
    db.session.add(lote)
    db.session.add(
        StockMovement(
            produto_id=produto.id,
            tipo="entrada",
            quantidade=qtd,
            usuario_id=current_user.id,
            motivo="Entrada rápida",
        )
    )
    db.session.commit()
    flash("Entrada rápida registrada.", "success")
    return _redirect_listar()
