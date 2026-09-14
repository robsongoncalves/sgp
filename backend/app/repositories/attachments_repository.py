from __future__ import annotations

import hashlib
from datetime import datetime
from pathlib import Path

from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.extensions import db
from app.models import ServiceRequest, ServiceRequestAttachment, ServiceRequestDocument, User
from app.repositories.utils import datetime_to_api, optional_int


class AttachmentsRepository:
    def list(self, service_request_id: int, filters: dict | None = None) -> list[dict]:
        query = ServiceRequestAttachment.query.filter(
            ServiceRequestAttachment.service_request_id == service_request_id,
        )

        filters = filters or {}
        context_type = str(filters.get("context_type", "")).strip()
        requirement_code = str(filters.get("requirement_code", "")).strip()
        item_index = optional_int(filters.get("item_index"))
        document_id = optional_int(filters.get("service_request_document_id"))

        if context_type:
            query = query.filter(ServiceRequestAttachment.context_type == context_type)

        if requirement_code:
            query = query.filter(ServiceRequestAttachment.requirement_code == requirement_code)

        if item_index is not None:
            query = query.filter(ServiceRequestAttachment.item_index == item_index)

        if document_id is not None:
            query = query.filter(ServiceRequestAttachment.service_request_document_id == document_id)

        attachments = query.order_by(ServiceRequestAttachment.created_at.desc()).all()
        return [self._to_dict(attachment) for attachment in attachments]

    def create(
        self,
        service_request_id: int,
        uploaded_by_user_id: int,
        file: FileStorage | None,
        data: dict,
    ) -> tuple[dict | None, str | None]:
        service_request = db.session.get(ServiceRequest, service_request_id)

        if service_request is None:
            return None, "Solicitacao nao encontrada."

        user = db.session.get(User, uploaded_by_user_id)

        if user is None:
            return None, "Usuario responsavel pelo upload nao encontrado."

        if file is None or not file.filename:
            return None, "Arquivo nao informado."

        document_id = optional_int(data.get("service_request_document_id"))
        document = db.session.get(ServiceRequestDocument, document_id) if document_id else None

        if document_id and (document is None or document.service_request_id != service_request.id):
            return None, "Documento da solicitacao nao encontrado."

        if current_app.config["ATTACHMENT_STORAGE_DRIVER"] != "local":
            return None, "Driver de armazenamento ainda nao suportado."

        original_name = Path(file.filename).name
        safe_name = secure_filename(original_name) or "arquivo"
        object_key = self._build_object_key(service_request_id, data, safe_name)
        target_path = self._local_root() / object_key
        target_path.parent.mkdir(parents=True, exist_ok=True)

        digest = hashlib.sha256()
        size_bytes = 0

        with target_path.open("wb") as output:
            while True:
                chunk = file.stream.read(1024 * 1024)

                if not chunk:
                    break

                size_bytes += len(chunk)
                digest.update(chunk)
                output.write(chunk)

        attachment = ServiceRequestAttachment(
            service_request_id=service_request.id,
            service_request_document_id=document.id if document else None,
            uploaded_by_user_id=user.id,
            original_name=original_name,
            mime_type=file.mimetype or "",
            size_bytes=size_bytes,
            bucket="local",
            object_key=object_key,
            sha256=digest.hexdigest(),
            context_type=str(data.get("context_type", "")).strip(),
            requirement_code=str(data.get("requirement_code", "")).strip(),
            item_index=optional_int(data.get("item_index")),
            description=str(data.get("description", "")).strip(),
        )

        db.session.add(attachment)
        db.session.commit()

        return self._to_dict(attachment), None

    def get(self, service_request_id: int, attachment_id: int) -> ServiceRequestAttachment | None:
        return ServiceRequestAttachment.query.filter(
            ServiceRequestAttachment.id == attachment_id,
            ServiceRequestAttachment.service_request_id == service_request_id,
        ).first()

    def delete(self, service_request_id: int, attachment_id: int) -> bool:
        attachment = self.get(service_request_id, attachment_id)

        if attachment is None:
            return False

        if attachment.bucket == "local":
            path = self.local_path(attachment)

            if path.exists():
                path.unlink()

        db.session.delete(attachment)
        db.session.commit()
        return True

    def local_path(self, attachment: ServiceRequestAttachment) -> Path:
        return self._local_root() / attachment.object_key

    def _build_object_key(self, service_request_id: int, data: dict, safe_name: str) -> str:
        context_type = secure_filename(str(data.get("context_type", "")).strip()) or "geral"
        requirement_code = secure_filename(str(data.get("requirement_code", "")).strip()) or "geral"
        item_index = optional_int(data.get("item_index"))
        item_folder = str(item_index) if item_index is not None else "geral"
        timestamp = datetime.utcnow().strftime("%Y%m%d-%H%M%S-%f")

        return str(
            Path("service-requests")
            / str(service_request_id)
            / context_type
            / requirement_code
            / item_folder
            / f"{timestamp}-{safe_name}"
        )

    def _local_root(self) -> Path:
        configured_path = Path(current_app.config["ATTACHMENT_LOCAL_PATH"])

        if configured_path.is_absolute():
            return configured_path

        return Path(current_app.root_path).parent / configured_path

    def _to_dict(self, attachment: ServiceRequestAttachment) -> dict:
        return {
            "id": attachment.id,
            "service_request_id": attachment.service_request_id,
            "service_request_document_id": attachment.service_request_document_id,
            "uploaded_by_user_id": attachment.uploaded_by_user_id,
            "uploaded_by_name": attachment.uploaded_by.name if attachment.uploaded_by else "",
            "original_name": attachment.original_name,
            "mime_type": attachment.mime_type,
            "size_bytes": attachment.size_bytes,
            "bucket": attachment.bucket,
            "object_key": attachment.object_key,
            "sha256": attachment.sha256,
            "context_type": attachment.context_type,
            "requirement_code": attachment.requirement_code,
            "item_index": attachment.item_index,
            "description": attachment.description,
            "created_at": datetime_to_api(attachment.created_at),
            "updated_at": datetime_to_api(attachment.updated_at),
        }


attachments_repository = AttachmentsRepository()
