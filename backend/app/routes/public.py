from flask import Blueprint, jsonify

from app.repositories.services_repository import services_repository

public_bp = Blueprint("public", __name__)


@public_bp.get("/public/services")
def list_public_services():
    return jsonify(services_repository.list_public())
