from flask import Flask

from config import Config
from .extensions import bootstrap, db, login_manager, migrate


def create_app(config_class=Config) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    bootstrap.init_app(app)

    from .routes.admin import admin_bp
    from .routes.auth import auth_bp
    from .routes.estoque import estoque_bp
    from .routes.main import main_bp
    from .routes.relatorios import relatorios_bp
    from .routes.vendas import vendas_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(estoque_bp, url_prefix="/estoque")
    app.register_blueprint(vendas_bp, url_prefix="/vendas")
    app.register_blueprint(relatorios_bp, url_prefix="/relatorios")
    app.register_blueprint(admin_bp, url_prefix="/admin")

    return app
