from flask import Flask
from flask_cors import CORS

from app.routes.health import health_bp
from app.routes.users import users_bp


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app)

    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(users_bp, url_prefix="/api")

    return app
