from flask import Blueprint, jsonify, request, send_file

from app.repositories.attachments_repository import attachments_repository
from app.repositories.service_request_documents_repository import service_request_documents_repository
from app.repositories.service_requests_repository import service_requests_repository

service_requests_bp = Blueprint("service_requests", __name__)


@service_requests_bp.get("/service-requests")
def list_service_requests():
    requester_user_id = request.args.get("requester_user_id", type=int)
    group_id = request.args.get("group_id", type=int)
    service_slug = request.args.get("service_slug", "")
    status = request.args.get("status", "")
    return jsonify(
        service_requests_repository.list(
            requester_user_id=requester_user_id,
            group_id=group_id,
            service_slug=service_slug,
            status=status,
        )
    )


@service_requests_bp.post("/service-requests")
def create_service_request():
    service_request, error, created = service_requests_repository.create(
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Servico nao encontrado." else 400
        return jsonify({"message": error}), status_code

    return jsonify(service_request), 201 if created else 200


@service_requests_bp.get("/service-requests/<int:service_request_id>")
def get_service_request(service_request_id: int):
    service_request = service_requests_repository.get(service_request_id)

    if service_request is None:
        return jsonify({"message": "Solicitacao nao encontrada."}), 404

    return jsonify(service_request)


@service_requests_bp.patch("/service-requests/<int:service_request_id>/form-data")
def update_service_request_form_data(service_request_id: int):
    payload = request.get_json(silent=True)

    if payload is None:
        payload = {}

    if not isinstance(payload, dict):
        return jsonify({"message": "Payload deve ser um objeto."}), 400

    form_data = payload.get("form_data", payload)

    if not isinstance(form_data, dict):
        return jsonify({"message": "Dados do formulario devem ser um objeto."}), 400

    service_request, error = service_requests_repository.update_form_data(
        service_request_id=service_request_id,
        form_data=form_data,
    )

    if error:
        return jsonify({"message": error}), 404

    return jsonify(service_request)


@service_requests_bp.patch("/service-requests/<int:service_request_id>/situation")
def update_service_request_situation(service_request_id: int):
    payload = request.get_json(silent=True) or {}
    situation_id = int(payload["situation_id"]) if payload.get("situation_id") else None
    service_request, error = service_requests_repository.update_situation(
        service_request_id=service_request_id,
        situation_id=situation_id,
        situation_name=str(payload.get("situation_name", "")).strip(),
    )

    if error:
        status_code = 404 if "nao encontrada" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(service_request)


@service_requests_bp.get("/service-requests/<int:service_request_id>/documents")
def list_service_request_documents(service_request_id: int):
    return jsonify(service_request_documents_repository.list(service_request_id))


@service_requests_bp.get("/service-request-documents")
def list_assigned_service_request_documents():
    assigned_to_user_id = request.args.get("assigned_to_user_id", type=int)

    if not assigned_to_user_id:
        return jsonify({"message": "Informe o usuario destinatario."}), 400

    return jsonify(service_request_documents_repository.list_assigned_to_user(assigned_to_user_id))


@service_requests_bp.post("/service-requests/<int:service_request_id>/documents")
def create_service_request_document(service_request_id: int):
    document, error = service_request_documents_repository.create(
        service_request_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if "nao encontrad" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(document), 201


@service_requests_bp.put("/service-requests/<int:service_request_id>/documents/<int:document_id>")
def update_service_request_document(service_request_id: int, document_id: int):
    document, error = service_request_documents_repository.update(
        service_request_id,
        document_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if "nao encontrad" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(document)


@service_requests_bp.post("/service-requests/<int:service_request_id>/documents/<int:document_id>/submit")
def submit_service_request_document(service_request_id: int, document_id: int):
    document, error = service_request_documents_repository.submit(
        service_request_id,
        document_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if "nao encontrad" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(document)


@service_requests_bp.post("/service-requests/<int:service_request_id>/documents/<int:document_id>/decision")
def decide_service_request_document(service_request_id: int, document_id: int):
    document, error = service_request_documents_repository.decide(
        service_request_id,
        document_id,
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if "nao encontrad" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(document)


@service_requests_bp.delete("/service-requests/<int:service_request_id>/documents/<int:document_id>")
def delete_service_request_document(service_request_id: int, document_id: int):
    user_id = request.args.get("user_id", type=int) or 0
    deleted, error = service_request_documents_repository.delete(service_request_id, document_id, user_id)

    if error:
        status_code = 404 if "nao encontrad" in error else 400
        return jsonify({"message": error}), status_code

    return "", 204 if deleted else 404


@service_requests_bp.post("/service-requests/<int:service_request_id>/documents/<int:document_id>/attachments")
def upload_service_request_document_attachment(service_request_id: int, document_id: int):
    data = request.form.to_dict()
    data["service_request_document_id"] = str(document_id)
    data["context_type"] = data.get("context_type") or "documento"

    attachment, error = attachments_repository.create(
        service_request_id=service_request_id,
        uploaded_by_user_id=request.form.get("uploaded_by_user_id", type=int) or 0,
        file=request.files.get("file"),
        data=data,
    )

    if error:
        status_code = 404 if "nao encontrada" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(attachment), 201


@service_requests_bp.get("/service-requests/<int:service_request_id>/attachments")
def list_service_request_attachments(service_request_id: int):
    return jsonify(
        attachments_repository.list(
            service_request_id,
            {
                "context_type": request.args.get("context_type", ""),
                "requirement_code": request.args.get("requirement_code", ""),
                "item_index": request.args.get("item_index", ""),
                "service_request_document_id": request.args.get("service_request_document_id", ""),
            },
        )
    )


@service_requests_bp.post("/service-requests/<int:service_request_id>/attachments")
def upload_service_request_attachment(service_request_id: int):
    attachment, error = attachments_repository.create(
        service_request_id=service_request_id,
        uploaded_by_user_id=request.form.get("uploaded_by_user_id", type=int) or 0,
        file=request.files.get("file"),
        data=request.form.to_dict(),
    )

    if error:
        status_code = 404 if "nao encontrada" in error else 400
        return jsonify({"message": error}), status_code

    return jsonify(attachment), 201


@service_requests_bp.get("/service-requests/<int:service_request_id>/attachments/<int:attachment_id>/download")
def download_service_request_attachment(service_request_id: int, attachment_id: int):
    attachment = attachments_repository.get(service_request_id, attachment_id)

    if attachment is None:
        return jsonify({"message": "Anexo nao encontrado."}), 404

    if attachment.bucket != "local":
        return jsonify({"message": "Driver de armazenamento ainda nao suportado."}), 400

    path = attachments_repository.local_path(attachment)

    if not path.exists():
        return jsonify({"message": "Arquivo fisico nao encontrado."}), 404

    return send_file(
        path,
        mimetype=attachment.mime_type or None,
        as_attachment=True,
        download_name=attachment.original_name,
    )


@service_requests_bp.delete("/service-requests/<int:service_request_id>/attachments/<int:attachment_id>")
def delete_service_request_attachment(service_request_id: int, attachment_id: int):
    deleted = attachments_repository.delete(service_request_id, attachment_id)

    if not deleted:
        return jsonify({"message": "Anexo nao encontrado."}), 404

    return "", 204
