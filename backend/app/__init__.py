from flask import Flask
from flask_cors import CORS

from app.routes.health import health_bp
from app.routes.service_categories import service_categories_bp
from app.routes.service_requests import service_requests_bp
from app.routes.services import services_bp
from app.routes.user_groups import user_groups_bp
from app.routes.users import users_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(service_categories_bp, url_prefix="/api")
    app.register_blueprint(service_requests_bp, url_prefix="/api")
    app.register_blueprint(services_bp, url_prefix="/api")
    app.register_blueprint(user_groups_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")

    return app
