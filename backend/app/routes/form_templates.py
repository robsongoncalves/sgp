from flask import Blueprint, jsonify, request

from app.repositories.form_templates_repository import form_templates_repository

form_templates_bp = Blueprint("form_templates", __name__)


@form_templates_bp.get("/form-templates")
def list_form_templates():
    return jsonify(form_templates_repository.list())


@form_templates_bp.post("/form-templates")
def create_form_template():
    template, error = form_templates_repository.create(request.get_json(silent=True) or {})

    if error:
        return jsonify({"message": error}), 400

    return jsonify(template), 201


@form_templates_bp.put("/form-templates/<int:template_id>")
def update_form_template(template_id: int):
    template, error = form_templates_repository.update(
        template_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Formulario nao encontrado." else 400
        return jsonify({"message": error}), status_code

    return jsonify(template)


@form_templates_bp.delete("/form-templates/<int:template_id>")
def delete_form_template(template_id: int):
    if not form_templates_repository.delete(template_id):
        return jsonify({"message": "Formulario nao encontrado."}), 404

    return "", 204
