from flask import Blueprint, jsonify, request

from app.repositories.automation_functions_repository import automation_functions_repository

automation_functions_bp = Blueprint("automation_functions", __name__)


@automation_functions_bp.get("/automation-functions")
def list_automation_functions():
    return jsonify(automation_functions_repository.list())


@automation_functions_bp.post("/automation-functions")
def create_automation_function():
    function, error = automation_functions_repository.create(
        request.get_json(silent=True) or {},
    )

    if error:
        return jsonify({"message": error}), 400

    return jsonify(function), 201


@automation_functions_bp.put("/automation-functions/<int:function_id>")
def update_automation_function(function_id: int):
    function, error = automation_functions_repository.update(
        function_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Function nao encontrada." else 400
        return jsonify({"message": error}), status_code

    return jsonify(function)


@automation_functions_bp.delete("/automation-functions/<int:function_id>")
def delete_automation_function(function_id: int):
    if not automation_functions_repository.delete(function_id):
        return jsonify({"message": "Function nao encontrada."}), 404

    return "", 204
