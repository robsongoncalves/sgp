from flask import Blueprint, jsonify, request

from app.documentation_extractor import extract_documentation_sections
from app.repositories.service_ratings_repository import service_ratings_repository
from app.repositories.services_repository import services_repository
from app.repositories.utils import optional_int

services_bp = Blueprint("services", __name__)


@services_bp.get("/services")
def list_services():
    return jsonify(services_repository.list())


@services_bp.post("/services")
def create_service():
    service, error = services_repository.create(
        request.get_json(silent=True) or {},
    )

    if error:
        return jsonify({"message": error}), 400

    return jsonify(service), 201


@services_bp.put("/services/<int:service_id>")
def update_service(service_id: int):
    service, error = services_repository.update(
        service_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Servico nao encontrado." else 400
        return jsonify({"message": error}), status_code

    return jsonify(service)


@services_bp.delete("/services/<int:service_id>")
def delete_service(service_id: int):
    if not services_repository.delete(service_id):
        return jsonify({"message": "Servico nao encontrado."}), 404

    return "", 204


@services_bp.post("/services/documentation/extract")
def extract_service_documentation():
    content, error = extract_documentation_sections(request.get_json(silent=True) or {})

    if error:
        return jsonify({"message": error}), 400

    return jsonify(content)


@services_bp.get("/services/<int:service_id>/ratings")
def get_service_ratings(service_id: int):
    summary, error = service_ratings_repository.summary(
        service_id,
        user_id=optional_int(request.args.get("user_id")),
    )

    if error:
        return jsonify({"message": error}), 404

    return jsonify(summary)


@services_bp.post("/services/<int:service_id>/ratings")
def save_service_rating(service_id: int):
    rating, error = service_ratings_repository.upsert(
        service_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error in {"Servico nao encontrado.", "Usuario nao encontrado."} else 400
        return jsonify({"message": error}), status_code

    return jsonify(rating)
