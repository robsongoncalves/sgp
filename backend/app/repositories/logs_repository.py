from __future__ import annotations

from app.models import ServiceHookExecution
from app.repositories.utils import datetime_to_api


class LogsRepository:
    def list_automation_logs(self, limit: int = 300) -> list[dict]:
        executions = ServiceHookExecution.query.order_by(
            ServiceHookExecution.created_at.desc(),
            ServiceHookExecution.id.desc(),
        ).limit(limit).all()

        return [self._automation_log_to_dict(execution) for execution in executions]

    def _automation_log_to_dict(self, execution: ServiceHookExecution) -> dict:
        hook = execution.hook
        service = hook.service if hook else None
        function = hook.function if hook else None
        service_request = execution.service_request

        return {
            "id": execution.id,
            "created_at": datetime_to_api(execution.created_at),
            "event_name": execution.event_name,
            "status": execution.status,
            "duration_ms": execution.duration_ms,
            "messages": execution.messages or [],
            "warnings": execution.warnings or [],
            "error_message": execution.error_message,
            "service_id": service.id if service else None,
            "service_name": service.name if service else "",
            "service_slug": service.slug if service else "",
            "function_id": function.id if function else None,
            "function_name": function.name if function else "",
            "handler_key": hook.handler_key if hook else "",
            "service_request_id": service_request.id if service_request else None,
            "service_request_number": service_request.number if service_request else "",
            "user_id": execution.user_id,
            "user_name": execution.user.name if execution.user else "",
            "user_email": execution.user.email if execution.user else "",
        }


logs_repository = LogsRepository()
