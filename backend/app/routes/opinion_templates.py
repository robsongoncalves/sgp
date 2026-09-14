from flask import Blueprint, jsonify, request

from app.repositories.opinion_templates_repository import opinion_templates_repository

opinion_templates_bp = Blueprint("opinion_templates", __name__)


@opinion_templates_bp.get("/opinion-templates")
def list_opinion_templates():
    return jsonify(opinion_templates_repository.list())


@opinion_templates_bp.post("/opinion-templates")
def create_opinion_template():
    template, error = opinion_templates_repository.create(request.get_json(silent=True) or {})

    if error:
        return jsonify({"message": error}), 400

    return jsonify(template), 201


@opinion_templates_bp.put("/opinion-templates/<int:template_id>")
def update_opinion_template(template_id: int):
    template, error = opinion_templates_repository.update(
        template_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Modelo de parecer nao encontrado." else 400
        return jsonify({"message": error}), status_code

    return jsonify(template)


@opinion_templates_bp.delete("/opinion-templates/<int:template_id>")
def delete_opinion_template(template_id: int):
    if not opinion_templates_repository.delete(template_id):
        return jsonify({"message": "Modelo de parecer nao encontrado."}), 404

    return "", 204
