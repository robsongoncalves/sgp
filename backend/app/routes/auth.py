from flask import Blueprint, jsonify, request

from app.repositories.users_repository import users_repository

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    user, error = users_repository.authenticate(
        payload.get("email", payload.get("username", "")),
        payload.get("password", ""),
    )

    if error:
        return jsonify({"message": error}), 401

    return jsonify({"user": user})
