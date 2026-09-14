from flask import Blueprint, jsonify, request

from app.repositories.document_types_repository import document_types_repository

document_types_bp = Blueprint("document_types", __name__)


@document_types_bp.get("/document-types")
def list_document_types():
    return jsonify(document_types_repository.list())


@document_types_bp.post("/document-types")
def create_document_type():
    document_type, error = document_types_repository.create(
        request.get_json(silent=True) or {},
    )

    if error:
        return jsonify({"message": error}), 400

    return jsonify(document_type), 201


@document_types_bp.put("/document-types/<int:document_type_id>")
def update_document_type(document_type_id: int):
    document_type, error = document_types_repository.update(
        document_type_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Tipo de documento nao encontrado." else 400
        return jsonify({"message": error}), status_code

    return jsonify(document_type)


@document_types_bp.delete("/document-types/<int:document_type_id>")
def delete_document_type(document_type_id: int):
    if not document_types_repository.delete(document_type_id):
        return jsonify({"message": "Tipo de documento nao encontrado."}), 404

    return "", 204
