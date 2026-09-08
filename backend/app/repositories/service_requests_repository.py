from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models import Service, ServiceRequest, User, UserGroup
from app.repositories.utils import datetime_to_api, optional_int

DEV_REQUESTER_USER_ID = 3


class ServiceRequestsRepository:
    def list(
        self,
        requester_user_id: int | None = None,
        group_id: int | None = None,
    ) -> list[dict]:
        query = ServiceRequest.query

        if requester_user_id is not None:
            query = query.filter(ServiceRequest.requester_user_id == requester_user_id)

        if group_id is not None:
            query = query.filter(
                ServiceRequest.service.has(Service.groups.any(UserGroup.id == group_id))
            )

        requests = query.order_by(ServiceRequest.created_at.desc()).all()
        return [self._to_dict(service_request) for service_request in requests]

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        service = self._find_service(data)

        if service is None:
            return None, "Servico nao encontrado."

        if not service.active:
            return None, "Servico inativo."

        requester_user_id = optional_int(data.get("requester_user_id")) or DEV_REQUESTER_USER_ID
        requester = db.session.get(User, requester_user_id)

        if requester is None:
            return None, "Usuario solicitante nao encontrado."

        initial_situation = next(
            (situation for situation in service.situations if situation.is_initial),
            service.situations[0] if service.situations else None,
        )
        service_request = ServiceRequest(
            number="",
            service_id=service.id,
            requester_user_id=requester.id,
            current_situation_id=initial_situation.id if initial_situation else None,
            status=initial_situation.name if initial_situation else "Solicitado",
            form_data={},
        )
        db.session.add(service_request)
        db.session.flush()
        service_request.number = self._request_number(service_request.id)
        db.session.commit()

        return self._to_dict(service_request), None

    def _find_service(self, data: dict) -> Service | None:
        service_id = optional_int(data.get("service_id"))
        service_slug = str(data.get("service_slug", "")).strip()

        if service_id is not None:
            return db.session.get(Service, service_id)

        if service_slug:
            return Service.query.filter(Service.slug == service_slug).first()

        return None

    def _to_dict(self, service_request: ServiceRequest) -> dict:
        service = service_request.service
        current_situation = service_request.current_situation

        return {
            "id": service_request.id,
            "number": service_request.number,
            "service_id": service_request.service_id,
            "service_name": service.name if service else "",
            "service_slug": service.slug if service else "",
            "module_key": service.module_key if service else "",
            "requester_user_id": service_request.requester_user_id,
            "requester_name": service_request.requester.name if service_request.requester else "",
            "requester_email": service_request.requester.email if service_request.requester else "",
            "current_situation_id": service_request.current_situation_id,
            "current_situation_name": current_situation.name if current_situation else service_request.status,
            "status": service_request.status,
            "created_at": datetime_to_api(service_request.created_at),
            "updated_at": datetime_to_api(service_request.updated_at),
            "canceled_at": datetime_to_api(service_request.canceled_at) if service_request.canceled_at else None,
        }

    def _request_number(self, request_id: int) -> str:
        return f"{datetime.now():%Y%m%d}{request_id:05d}"


service_requests_repository = ServiceRequestsRepository()
