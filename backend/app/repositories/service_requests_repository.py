from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models import Service, ServiceRequest, ServiceRequestMovement, User, UserGroup
from app.repositories.utils import datetime_to_api, optional_int
from app.service_hooks import service_hook_runner

DEV_REQUESTER_USER_ID = 3


class ServiceRequestsRepository:
    def cancel(self, service_request_id: int, user_id: int):
        item = ServiceRequest.query.filter_by(id=service_request_id).with_for_update().first()
        if item is None:
            return None, "Solicitacao nao encontrada.", 404
        user = db.session.get(User, user_id)
        if user is None or item.requester_user_id != user.id:
            return None, "Somente o solicitante pode cancelar esta solicitacao.", 403
        if item.canceled_at:
            return self._to_dict(item), None, 200
        if item.current_situation and item.current_situation.is_final:
            return None, "Uma solicitacao concluida nao pode ser cancelada.", 409
        item.canceled_at = datetime.utcnow()
        item.canceled_by_user_id = user.id
        db.session.add(ServiceRequestMovement(
            service_request_id=item.id,
            from_situation_id=item.current_situation_id,
            to_situation_id=None,
            moved_by_user_id=user.id,
            opinion=f"Solicitacao cancelada pelo solicitante. Situacao anterior: {item.status}.",
        ))
        db.session.commit()
        return self._to_dict(item), None, 200

    def get(self, service_request_id: int) -> dict | None:
        service_request = db.session.get(ServiceRequest, service_request_id)

        if service_request is None:
            return None

        return self._to_dict(service_request)

    def list(
        self,
        requester_user_id: int | None = None,
        group_id: int | None = None,
        service_slug: str = "",
        status: str = "",
    ) -> list[dict]:
        query = ServiceRequest.query

        if requester_user_id is not None:
            query = query.filter(ServiceRequest.requester_user_id == requester_user_id)

        if group_id is not None:
            query = query.filter(
                ServiceRequest.service.has(Service.groups.any(UserGroup.id == group_id))
            )

        if service_slug:
            query = query.filter(ServiceRequest.service.has(Service.slug == service_slug))

        if status == 'Cancelada':
            query = query.filter(ServiceRequest.canceled_at.is_not(None))
        elif status:
            query = query.filter(ServiceRequest.status == status, ServiceRequest.canceled_at.is_(None))

        requests = query.order_by(ServiceRequest.created_at.desc()).all()
        return [self._to_dict(service_request) for service_request in requests]

    def create(self, data: dict) -> tuple[dict | None, str | None, bool]:
        service = self._find_service(data)

        if service is None:
            return None, "Servico nao encontrado.", False

        if not service.active:
            return None, "Servico inativo.", False

        requester_user_id = optional_int(data.get("requester_user_id")) or DEV_REQUESTER_USER_ID
        requester = db.session.get(User, requester_user_id)

        if requester is None:
            return None, "Usuario solicitante nao encontrado.", False

        initial_situation = next(
            (situation for situation in service.situations if situation.is_initial),
            service.situations[0] if service.situations else None,
        )

        existing_initial_request = self._find_existing_initial_request(
            service_id=service.id,
            requester_user_id=requester.id,
            initial_situation_id=initial_situation.id if initial_situation else None,
            initial_status=initial_situation.name if initial_situation else "Solicitado",
        )

        if existing_initial_request is not None:
            hook_result = service_hook_runner.run(
                event_name="before_request_create",
                service=service,
                user=requester,
                service_request=existing_initial_request,
                form_data=existing_initial_request.form_data or {},
            )
            existing_initial_request.form_data = hook_result["form_data"]
            db.session.commit()
            return self._to_dict(existing_initial_request), None, False

        hook_result = service_hook_runner.run(
            event_name="before_request_create",
            service=service,
            user=requester,
            form_data=data.get("form_data", {}),
        )

        service_request = ServiceRequest(
            number="",
            service_id=service.id,
            requester_user_id=requester.id,
            current_situation_id=initial_situation.id if initial_situation else None,
            status=initial_situation.name if initial_situation else "Solicitado",
            form_data=hook_result["form_data"],
        )
        db.session.add(service_request)
        db.session.flush()
        service_request.number = self._request_number(service_request.id)

        service_hook_runner.run(
            event_name="after_request_create",
            service=service,
            user=requester,
            service_request=service_request,
            form_data=service_request.form_data,
        )

        db.session.commit()

        return self._to_dict(service_request), None, True

    def update_situation(
        self,
        service_request_id: int,
        situation_id: int | None = None,
        situation_name: str = "",
    ) -> tuple[dict | None, str | None]:
        service_request = db.session.get(ServiceRequest, service_request_id)

        if service_request is None:
            return None, "Solicitacao nao encontrada."

        situation = next(
            (
                item
                for item in service_request.service.situations
                if (
                    (situation_id is not None and item.id == situation_id)
                    or (situation_name and item.name == situation_name)
                )
            ),
            None,
        )

        if situation is None:
            return None, "Situacao nao encontrada para este servico."

        service_request.current_situation_id = situation.id
        service_request.status = situation.name
        db.session.commit()

        return self._to_dict(service_request), None

    def update_form_data(self, service_request_id: int, form_data: dict) -> tuple[dict | None, str | None]:
        service_request = db.session.get(ServiceRequest, service_request_id)

        if service_request is None:
            return None, "Solicitacao nao encontrada."

        service_request.form_data = form_data
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

    def _find_existing_initial_request(
        self,
        service_id: int,
        requester_user_id: int,
        initial_situation_id: int | None,
        initial_status: str,
    ) -> ServiceRequest | None:
        query = ServiceRequest.query.filter(
            ServiceRequest.service_id == service_id,
            ServiceRequest.requester_user_id == requester_user_id,
            ServiceRequest.canceled_at.is_(None),
        )

        if initial_situation_id is not None:
            query = query.filter(ServiceRequest.current_situation_id == initial_situation_id)
        else:
            query = query.filter(
                ServiceRequest.current_situation_id.is_(None),
                ServiceRequest.status == initial_status,
            )

        return query.order_by(ServiceRequest.created_at.desc()).first()

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
            "current_situation_name": "Cancelada" if service_request.canceled_at else service_request.status,
            "status": "Cancelada" if service_request.canceled_at else service_request.status,
            "situation_before_cancellation": service_request.status if service_request.canceled_at else None,
            "is_final": bool(current_situation and current_situation.is_final),
            "form_data": service_request.form_data or {},
            "created_at": datetime_to_api(service_request.created_at),
            "updated_at": datetime_to_api(service_request.updated_at),
            "canceled_at": datetime_to_api(service_request.canceled_at) if service_request.canceled_at else None,
            "canceled_by_user_id": service_request.canceled_by_user_id,
            "canceled_by_name": service_request.canceled_by.name if service_request.canceled_by else None,
        }

    def _request_number(self, request_id: int) -> str:
        return f"{datetime.now():%Y%m%d}{request_id:05d}"


service_requests_repository = ServiceRequestsRepository()
