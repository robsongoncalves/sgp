from flask import Blueprint, jsonify, request

from app.repositories.service_categories_repository import service_categories_repository

service_categories_bp = Blueprint("service_categories", __name__)


@service_categories_bp.get("/service-categories")
def list_service_categories():
    return jsonify(service_categories_repository.list())


@service_categories_bp.post("/service-categories")
def create_service_category():
    category, error = service_categories_repository.create(
        request.get_json(silent=True) or {},
    )

    if error:
        return jsonify({"message": error}), 400

    return jsonify(category), 201


@service_categories_bp.put("/service-categories/<int:category_id>")
def update_service_category(category_id: int):
    category, error = service_categories_repository.update(
        category_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Categoria nao encontrada." else 400
        return jsonify({"message": error}), status_code

    return jsonify(category)


@service_categories_bp.delete("/service-categories/<int:category_id>")
def delete_service_category(category_id: int):
    if not service_categories_repository.delete(category_id):
        return jsonify({"message": "Categoria nao encontrada."}), 404

    return "", 204
