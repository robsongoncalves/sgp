from flask import Blueprint, jsonify, request

from app.repositories.logs_repository import logs_repository
from app.repositories.utils import optional_int

logs_bp = Blueprint("logs", __name__)


@logs_bp.get("/logs/automation")
def list_automation_logs():
    limit = optional_int(request.args.get("limit")) or 300
    limit = min(max(limit, 1), 1000)

    return jsonify(logs_repository.list_automation_logs(limit=limit))
