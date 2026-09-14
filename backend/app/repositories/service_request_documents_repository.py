from __future__ import annotations

from datetime import datetime

from app.extensions import db
from app.models import (
    DocumentType,
    ServiceRequest,
    ServiceRequestDocument,
    ServiceSituation,
    User,
    user_group_members,
)
from app.repositories.utils import bool_value, datetime_to_api, optional_int


class ServiceRequestDocumentsRepository:
    def list(self, service_request_id: int) -> list[dict]:
        documents = ServiceRequestDocument.query.filter(
            ServiceRequestDocument.service_request_id == service_request_id,
            ServiceRequestDocument.deleted_at.is_(None),
        ).order_by(
            ServiceRequestDocument.created_at.desc(),
        ).all()

        return [self._to_dict(document) for document in documents]

    def list_assigned_to_user(self, user_id: int) -> list[dict]:
        documents = ServiceRequestDocument.query.filter(
            ServiceRequestDocument.assigned_to_user_id == user_id,
            ServiceRequestDocument.status == "submitted",
            ServiceRequestDocument.deleted_at.is_(None),
        ).order_by(
            ServiceRequestDocument.updated_at.desc(),
        ).all()

        return [self._to_dict(document) for document in documents]

    def get(self, service_request_id: int, document_id: int) -> ServiceRequestDocument | None:
        return ServiceRequestDocument.query.filter(
            ServiceRequestDocument.id == document_id,
            ServiceRequestDocument.service_request_id == service_request_id,
            ServiceRequestDocument.deleted_at.is_(None),
        ).first()

    def create(self, service_request_id: int, data: dict) -> tuple[dict | None, str | None]:
        service_request, situation, document_type, user, error = self._validate_base(
            service_request_id,
            data,
        )

        if error:
            return None, error

        permission_error = self._validate_permission(service_request, situation, document_type, user)
        if permission_error:
            return None, permission_error

        if (
            not document_type.allow_multiple_files
            and self._active_document_exists(service_request.id, situation.id, document_type.id)
        ):
            return None, "Ja existe um documento ativo deste tipo para esta situacao."

        content_data = data.get("content_data", {})
        if not isinstance(content_data, dict):
            return None, "Dados do documento devem ser um objeto."

        linked_service_request_id = optional_int(data.get("linked_service_request_id"))
        if linked_service_request_id is not None:
            link_error = self._validate_linked_service_request(
                service_request,
                document_type,
                linked_service_request_id,
            )
            if link_error:
                return None, link_error

        document = ServiceRequestDocument(
            service_request_id=service_request.id,
            service_situation_id=situation.id,
            document_type_id=document_type.id,
            linked_service_request_id=linked_service_request_id,
            created_by_user_id=user.id,
            updated_by_user_id=user.id,
            status=(
                "linked"
                if document_type.purpose == "linked_service" and linked_service_request_id
                else str(data.get("status", "draft")).strip() or "draft"
            ),
            content_data=content_data,
        )
        db.session.add(document)
        db.session.commit()

        return self._to_dict(document), None

    def update(self, service_request_id: int, document_id: int, data: dict) -> tuple[dict | None, str | None]:
        document = self.get(service_request_id, document_id)
        if document is None:
            return None, "Documento da solicitacao nao encontrado."

        user = db.session.get(User, optional_int(data.get("updated_by_user_id")) or 0)
        if user is None:
            return None, "Usuario responsavel pela atualizacao nao encontrado."

        permission_error = self._validate_permission(
            document.service_request,
            document.service_situation,
            document.document_type,
            user,
        )
        if permission_error:
            return None, permission_error

        if "content_data" in data:
            if not isinstance(data["content_data"], dict):
                return None, "Dados do documento devem ser um objeto."
            document.content_data = data["content_data"]

        if "status" in data:
            document.status = str(data.get("status", "draft")).strip() or "draft"

        if "assigned_to_user_id" in data:
            document.assigned_to_user_id = optional_int(data.get("assigned_to_user_id"))

        if "assigned_to_group_id" in data:
            document.assigned_to_group_id = optional_int(data.get("assigned_to_group_id"))

        if "linked_service_request_id" in data:
            linked_service_request_id = optional_int(data.get("linked_service_request_id"))
            if linked_service_request_id is not None:
                link_error = self._validate_linked_service_request(
                    document.service_request,
                    document.document_type,
                    linked_service_request_id,
                )
                if link_error:
                    return None, link_error
            document.linked_service_request_id = linked_service_request_id
            if document.document_type.purpose == "linked_service":
                document.status = "linked" if linked_service_request_id else "draft"

        document.updated_by_user_id = user.id
        db.session.commit()

        return self._to_dict(document), None

    def submit(self, service_request_id: int, document_id: int, data: dict) -> tuple[dict | None, str | None]:
        document = self.get(service_request_id, document_id)
        if document is None:
            return None, "Documento da solicitacao nao encontrado."

        user = db.session.get(User, optional_int(data.get("submitted_by_user_id")) or 0)
        if user is None:
            return None, "Usuario responsavel pelo envio nao encontrado."

        permission_error = self._validate_permission(
            document.service_request,
            document.service_situation,
            document.document_type,
            user,
        )
        if permission_error:
            return None, permission_error

        assigned_to_user_id = optional_int(data.get("assigned_to_user_id"))

        if assigned_to_user_id is None:
            assigned_to_user_id = self._mapped_assigned_user_id(document)

        if assigned_to_user_id is None:
            return None, "Informe o usuario destinatario do documento."

        if db.session.get(User, assigned_to_user_id) is None:
            return None, "Usuario destinatario nao encontrado."

        document.assigned_to_user_id = assigned_to_user_id
        document.status = "submitted"
        document.updated_by_user_id = user.id
        db.session.commit()

        return self._to_dict(document), None

    def decide(self, service_request_id: int, document_id: int, data: dict) -> tuple[dict | None, str | None]:
        document = self.get(service_request_id, document_id)
        if document is None:
            return None, "Documento da solicitacao nao encontrado."

        user = db.session.get(User, optional_int(data.get("decided_by_user_id")) or 0)
        if user is None:
            return None, "Usuario responsavel pela decisao nao encontrado."

        if document.assigned_to_user_id != user.id:
            return None, "Somente o usuario destinatario pode decidir este documento."

        decision = str(data.get("decision", "")).strip()
        if decision not in {"approved", "rejected", "returned"}:
            return None, "Informe uma decisao valida."

        document.decision = decision
        document.decision_text = str(data.get("decision_text", "")).strip()
        document.decided_by_user_id = user.id
        document.decided_at = datetime.utcnow()
        document.updated_by_user_id = user.id
        document.status = decision
        db.session.commit()

        return self._to_dict(document), None

    def delete(self, service_request_id: int, document_id: int, user_id: int) -> tuple[bool, str | None]:
        document = self.get(service_request_id, document_id)
        if document is None:
            return False, "Documento da solicitacao nao encontrado."

        user = db.session.get(User, user_id)
        if user is None:
            return False, "Usuario responsavel pela exclusao nao encontrado."

        permission_error = self._validate_permission(
            document.service_request,
            document.service_situation,
            document.document_type,
            user,
        )
        if permission_error:
            return False, permission_error

        document.deleted_at = datetime.utcnow()
        document.updated_by_user_id = user.id
        db.session.commit()
        return True, None

    def _validate_base(
        self,
        service_request_id: int,
        data: dict,
    ) -> tuple[ServiceRequest | None, ServiceSituation | None, DocumentType | None, User | None, str | None]:
        service_request = db.session.get(ServiceRequest, service_request_id)
        if service_request is None:
            return None, None, None, None, "Solicitacao nao encontrada."

        situation_id = optional_int(data.get("service_situation_id"))
        document_type_id = optional_int(data.get("document_type_id"))
        user_id = optional_int(data.get("created_by_user_id"))

        situation = db.session.get(ServiceSituation, situation_id) if situation_id else None
        if situation is None or situation.service_id != service_request.service_id:
            return service_request, None, None, None, "Situacao nao encontrada para este servico."

        document_type = db.session.get(DocumentType, document_type_id) if document_type_id else None
        if document_type is None:
            return service_request, situation, None, None, "Tipo de documento nao encontrado."

        if document_type not in situation.document_types:
            return service_request, situation, document_type, None, "Tipo de documento nao configurado nesta situacao."

        user = db.session.get(User, user_id) if user_id else None
        if user is None:
            return service_request, situation, document_type, None, "Usuario responsavel nao encontrado."

        return service_request, situation, document_type, user, None

    def _validate_permission(
        self,
        service_request: ServiceRequest,
        situation: ServiceSituation,
        document_type: DocumentType,
        user: User,
    ) -> str | None:
        if service_request.current_situation_id != situation.id:
            return "Documentos so podem ser alterados na situacao atual da solicitacao."

        if document_type.origin in {"system"} or document_type.purpose == "generated":
            return "Documento gerado pelo sistema nao pode ser criado manualmente."

        if document_type.origin in {"requester", "external"}:
            if service_request.requester_user_id != user.id:
                return "Somente o solicitante pode alterar este documento."
            return None

        if document_type.origin == "responsible_group":
            if not situation.responsible_group_id:
                return "Situacao sem grupo responsavel configurado."

            if not self._is_group_member(user.id, situation.responsible_group_id):
                return "Usuario nao faz parte do grupo responsavel pela situacao atual."

        return None

    def _is_group_member(self, user_id: int, group_id: int) -> bool:
        query = db.session.query(user_group_members).filter(
            user_group_members.c.user_id == user_id,
            user_group_members.c.group_id == group_id,
        )
        return db.session.query(query.exists()).scalar()

    def _mapped_assigned_user_id(self, document: ServiceRequestDocument) -> int | None:
        form_template = document.document_type.form_template

        if form_template is None:
            return None

        for field in form_template.fields_schema or []:
            if field.get("maps_to") != "assigned_to_user_id":
                continue

            return optional_int((document.content_data or {}).get(field.get("name", "")))

        return None

    def _validate_linked_service_request(
        self,
        service_request: ServiceRequest,
        document_type: DocumentType,
        linked_service_request_id: int,
    ) -> str | None:
        if document_type.purpose != "linked_service":
            return "Este tipo de documento nao aceita servico vinculado."

        if not document_type.linked_service_id:
            return "Tipo de documento sem servico vinculado configurado."

        linked_request = db.session.get(ServiceRequest, linked_service_request_id)

        if linked_request is None:
            return "Solicitacao vinculada nao encontrada."

        if linked_request.service_id != document_type.linked_service_id:
            return "Solicitacao vinculada pertence a outro servico."

        if linked_request.requester_user_id != service_request.requester_user_id:
            return "Solicitacao vinculada deve pertencer ao mesmo solicitante."

        return None

    def _active_document_exists(self, service_request_id: int, situation_id: int, document_type_id: int) -> bool:
        query = ServiceRequestDocument.query.filter(
            ServiceRequestDocument.service_request_id == service_request_id,
            ServiceRequestDocument.service_situation_id == situation_id,
            ServiceRequestDocument.document_type_id == document_type_id,
            ServiceRequestDocument.deleted_at.is_(None),
        )
        return db.session.query(query.exists()).scalar()

    def _to_dict(self, document: ServiceRequestDocument) -> dict:
        attachments = [attachment for attachment in document.attachments]

        return {
            "id": document.id,
            "service_request_id": document.service_request_id,
            "service_situation_id": document.service_situation_id,
            "service_situation_name": document.service_situation.name if document.service_situation else "",
            "document_type_id": document.document_type_id,
            "document_type_name": document.document_type.name if document.document_type else "",
            "linked_service_request_id": document.linked_service_request_id,
            "linked_service_request_number": (
                document.linked_service_request.number if document.linked_service_request else ""
            ),
            "linked_service_request_status": (
                document.linked_service_request.status if document.linked_service_request else ""
            ),
            "linked_service_request_service_slug": (
                document.linked_service_request.service.slug
                if document.linked_service_request and document.linked_service_request.service
                else ""
            ),
            "linked_service_request_module_key": (
                document.linked_service_request.service.module_key
                if document.linked_service_request and document.linked_service_request.service
                else ""
            ),
            "created_by_user_id": document.created_by_user_id,
            "created_by_name": document.created_by.name if document.created_by else "",
            "updated_by_user_id": document.updated_by_user_id,
            "updated_by_name": document.updated_by.name if document.updated_by else "",
            "assigned_to_user_id": document.assigned_to_user_id,
            "assigned_to_user_name": document.assigned_to_user.name if document.assigned_to_user else "",
            "assigned_to_user_email": document.assigned_to_user.email if document.assigned_to_user else "",
            "assigned_to_group_id": document.assigned_to_group_id,
            "assigned_to_group_name": document.assigned_to_group.name if document.assigned_to_group else "",
            "decided_by_user_id": document.decided_by_user_id,
            "decided_by_name": document.decided_by.name if document.decided_by else "",
            "decided_at": datetime_to_api(document.decided_at) if document.decided_at else None,
            "decision": document.decision,
            "decision_text": document.decision_text,
            "status": document.status,
            "content_data": document.content_data or {},
            "attachments_count": len(attachments),
            "created_at": datetime_to_api(document.created_at),
            "updated_at": datetime_to_api(document.updated_at),
            "deleted_at": datetime_to_api(document.deleted_at) if document.deleted_at else None,
        }


service_request_documents_repository = ServiceRequestDocumentsRepository()
