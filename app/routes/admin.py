from functools import wraps

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.models import Product, StockMovement, User


admin_bp = Blueprint("admin", __name__)

ROLES_PERMITIDAS = frozenset({"admin", "operador"})


def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not getattr(current_user, "is_admin", False):
            flash("Acesso negado.", "danger")
            return redirect(url_for("main.dashboard"))
        return view(*args, **kwargs)

    return wrapped


def _total_admins() -> int:
    return User.query.filter_by(role="admin").count()


@admin_bp.route("/")
@admin_required
def index():
    total_produtos = Product.query.count()
    total_movimentacoes = StockMovement.query.count()
    usuarios = User.query.order_by(User.id).all()
    return render_template(
        "admin/index.html",
        total_produtos=total_produtos,
        total_movimentacoes=total_movimentacoes,
        usuarios=usuarios,
        roles_permitidas=sorted(ROLES_PERMITIDAS),
    )


@admin_bp.route("/usuarios/criar", methods=["POST"])
@admin_required
def usuario_criar():
    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""
    role = (request.form.get("role") or "operador").strip()

    if not username or not password:
        flash("Usuário e senha são obrigatórios.", "warning")
        return redirect(url_for("admin.index"))
    if role not in ROLES_PERMITIDAS:
        flash("Papel inválido.", "danger")
        return redirect(url_for("admin.index"))
    if User.query.filter_by(username=username).first():
        flash("Já existe um usuário com esse nome.", "warning")
        return redirect(url_for("admin.index"))

    u = User(username=username, role=role)
    u.set_password(password)
    db.session.add(u)
    db.session.commit()
    flash("Usuário criado.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/usuarios/<int:user_id>/editar", methods=["POST"])
@admin_required
def usuario_editar(user_id: int):
    alvo = User.query.get_or_404(user_id)
    username = (request.form.get("username") or "").strip()
    password = (request.form.get("password") or "").strip()
    role = (request.form.get("role") or alvo.role).strip()

    if not username:
        flash("Nome de usuário não pode ficar vazio.", "warning")
        return redirect(url_for("admin.index"))
    if role not in ROLES_PERMITIDAS:
        flash("Papel inválido.", "danger")
        return redirect(url_for("admin.index"))

    outro = User.query.filter(User.username == username, User.id != alvo.id).first()
    if outro:
        flash("Já existe outro usuário com esse nome.", "warning")
        return redirect(url_for("admin.index"))

    if alvo.role == "admin" and role != "admin" and _total_admins() <= 1:
        flash("Não é possível rebaixar o único administrador.", "danger")
        return redirect(url_for("admin.index"))

    alvo.username = username
    alvo.role = role
    if password:
        alvo.set_password(password)
    db.session.commit()
    flash("Usuário atualizado.", "success")
    return redirect(url_for("admin.index"))


@admin_bp.route("/usuarios/<int:user_id>/excluir", methods=["POST"])
@admin_required
def usuario_excluir(user_id: int):
    alvo = User.query.get_or_404(user_id)
    if alvo.id == current_user.id:
        flash("Você não pode excluir a si mesmo enquanto estiver logado.", "warning")
        return redirect(url_for("admin.index"))
    if alvo.role == "admin" and _total_admins() <= 1:
        flash("Não é possível excluir o único administrador.", "danger")
        return redirect(url_for("admin.index"))

    db.session.delete(alvo)
    db.session.commit()
    flash("Usuário excluído.", "success")
    return redirect(url_for("admin.index"))
