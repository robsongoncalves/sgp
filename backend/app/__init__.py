from flask import Flask
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint

from app.cli import register_cli
from app.config import Config
from app.extensions import db, migrate
from app.openapi import OPENAPI_SPEC
from app.routes.auth import auth_bp
from app.routes.health import health_bp
from app.routes.document_types import document_types_bp
from app.routes.form_templates import form_templates_bp
from app.routes.opinion_templates import opinion_templates_bp
from app.routes.public import public_bp
from app.routes.service_categories import service_categories_bp
from app.routes.service_requests import service_requests_bp
from app.routes.services import services_bp
from app.routes.user_groups import user_groups_bp
from app.routes.users import users_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    from app import models  # noqa: F401

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(document_types_bp, url_prefix="/api")
    app.register_blueprint(form_templates_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(opinion_templates_bp, url_prefix="/api")
    app.register_blueprint(public_bp, url_prefix="/api")
    app.register_blueprint(service_categories_bp, url_prefix="/api")
    app.register_blueprint(service_requests_bp, url_prefix="/api")
    app.register_blueprint(services_bp, url_prefix="/api")
    app.register_blueprint(user_groups_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")

    @app.get("/api/openapi.json")
    def openapi_json():
        return OPENAPI_SPEC

    swaggerui_blueprint = get_swaggerui_blueprint(
        "/api/docs",
        "/api/openapi.json",
        config={"app_name": "SGP API"},
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix="/api/docs")
    register_cli(app)

    return app
