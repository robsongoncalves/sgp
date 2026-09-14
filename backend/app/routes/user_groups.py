from flask import Blueprint, jsonify, request

from app.repositories.user_groups_repository import user_groups_repository

user_groups_bp = Blueprint("user_groups", __name__)


@user_groups_bp.get("/user-groups")
def list_user_groups():
    user_id = request.args.get("user_id", type=int)

    if user_id is not None:
        groups = user_groups_repository.list_by_user(user_id)

        if groups is None:
            return jsonify({"message": "Usuario nao encontrado."}), 404

        return jsonify(groups)

    return jsonify(user_groups_repository.list())


@user_groups_bp.post("/user-groups")
def create_user_group():
    group, error = user_groups_repository.create(request.get_json(silent=True) or {})

    if error:
        return jsonify({"message": error}), 400

    return jsonify(group), 201


@user_groups_bp.put("/user-groups/<int:group_id>")
def update_user_group(group_id: int):
    group, error = user_groups_repository.update(
        group_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Unidade nao encontrada." else 400
        return jsonify({"message": error}), status_code

    return jsonify(group)


@user_groups_bp.delete("/user-groups/<int:group_id>")
def delete_user_group(group_id: int):
    if not user_groups_repository.delete(group_id):
        return jsonify({"message": "Unidade nao encontrada."}), 404

    return "", 204


@user_groups_bp.get("/user-groups/<int:group_id>/members")
def list_user_group_members(group_id: int):
    user_ids = user_groups_repository.get_member_user_ids(group_id)

    if user_ids is None:
        return jsonify({"message": "Unidade nao encontrada."}), 404

    return jsonify({"user_ids": user_ids})


@user_groups_bp.put("/user-groups/<int:group_id>/members")
def update_user_group_members(group_id: int):
    payload = request.get_json(silent=True) or {}
    user_ids = payload.get("user_ids", [])

    if not isinstance(user_ids, list):
        return jsonify({"message": "Informe uma lista de usuarios."}), 400

    updated_user_ids = user_groups_repository.set_member_user_ids(group_id, user_ids)

    if updated_user_ids is None:
        return jsonify({"message": "Unidade nao encontrada."}), 404

    return jsonify({"user_ids": updated_user_ids})
