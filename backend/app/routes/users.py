from flask import Blueprint, jsonify, request

from app.repositories.users_repository import users_repository

users_bp = Blueprint("users", __name__)


@users_bp.get("/users")
def list_users():
    return jsonify(users_repository.list())


@users_bp.post("/users")
def create_user():
    user, error = users_repository.create(request.get_json(silent=True) or {})

    if error:
        return jsonify({"message": error}), 400

    return jsonify(user), 201


@users_bp.put("/users/<int:user_id>")
def update_user(user_id: int):
    user, error = users_repository.update(user_id, request.get_json(silent=True) or {})

    if error:
        status_code = 404 if error == "Usuario nao encontrado." else 400
        return jsonify({"message": error}), status_code

    return jsonify(user)


@users_bp.delete("/users/<int:user_id>")
def delete_user(user_id: int):
    if not users_repository.delete(user_id):
        return jsonify({"message": "Usuario nao encontrado."}), 404

    return "", 204
