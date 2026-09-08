from flask import Blueprint, jsonify, request

from app.repositories.service_requests_repository import service_requests_repository

service_requests_bp = Blueprint("service_requests", __name__)


@service_requests_bp.get("/service-requests")
def list_service_requests():
    requester_user_id = request.args.get("requester_user_id", type=int)
    group_id = request.args.get("group_id", type=int)
    return jsonify(
        service_requests_repository.list(
            requester_user_id=requester_user_id,
            group_id=group_id,
        )
    )


@service_requests_bp.post("/service-requests")
def create_service_request():
    service_request, error = service_requests_repository.create(
        request.get_json(silent=True) or {},
    )

    if error:
        status_code = 404 if error == "Servico nao encontrado." else 400
        return jsonify({"message": error}), status_code

    return jsonify(service_request), 201
