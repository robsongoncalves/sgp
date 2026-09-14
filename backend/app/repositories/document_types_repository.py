from __future__ import annotations

import re
import unicodedata

from app.extensions import db
from app.models import DocumentType, FormTemplate, OpinionTemplate, Service
from app.repositories.utils import bool_value


class DocumentTypesRepository:
    def list(self) -> list[dict]:
        document_types = DocumentType.query.order_by(
            DocumentType.name.asc(),
        ).all()
        return [self._to_dict(document_type) for document_type in document_types]

    def get(self, document_type_id: int) -> DocumentType | None:
        return db.session.get(DocumentType, document_type_id)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        if self._name_exists(normalized_data["name"]):
            return None, "Ja existe um tipo de documento cadastrado com este nome."

        if self._code_exists(normalized_data["code"]):
            return None, "Ja existe um tipo de documento cadastrado com esta chave."

        document_type = DocumentType(**normalized_data)
        db.session.add(document_type)
        db.session.commit()

        return self._to_dict(document_type), None

    def update(self, document_type_id: int, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        document_type = self.get(document_type_id)

        if document_type is None:
            return None, "Tipo de documento nao encontrado."

        if self._name_exists(normalized_data["name"], ignore_document_type_id=document_type_id):
            return None, "Ja existe um tipo de documento cadastrado com este nome."

        if self._code_exists(normalized_data["code"], ignore_document_type_id=document_type_id):
            return None, "Ja existe um tipo de documento cadastrado com esta chave."

        for field, value in normalized_data.items():
            setattr(document_type, field, value)

        db.session.commit()

        return self._to_dict(document_type), None

    def delete(self, document_type_id: int) -> bool:
        document_type = self.get(document_type_id)

        if document_type is None:
            return False

        db.session.delete(document_type)
        db.session.commit()
        return True

    def _normalize(self, data: dict) -> dict:
        name = str(data.get("name", "")).strip()
        code = str(data.get("code", "")).strip() or self._slugify(name)

        return {
            "name": name,
            "code": self._slugify(code),
            "description": str(data.get("description", "")).strip(),
            "origin": str(data.get("origin", "requester")).strip() or "requester",
            "purpose": str(data.get("purpose", "attachment")).strip() or "attachment",
            "module_slug": str(data.get("module_slug", "")).strip(),
            "form_template_id": self._optional_int(data.get("form_template_id")),
            "opinion_template_id": self._optional_int(data.get("opinion_template_id")),
            "linked_service_id": self._optional_int(data.get("linked_service_id")),
            "linked_service_required_status": str(data.get("linked_service_required_status", "")).strip(),
            "allowed_formats": str(data.get("allowed_formats", "PDF")).strip() or "PDF",
            "required_by_default": bool_value(data.get("required_by_default", False)),
            "allow_multiple_files": bool_value(data.get("allow_multiple_files", False)),
            "active": bool_value(data.get("active", True)),
        }

    def _validate(self, data: dict) -> str | None:
        if not data["name"]:
            return "Informe o nome do tipo de documento."

        if not data["code"]:
            return "Informe a chave do tipo de documento."

        if data["origin"] not in {"requester", "responsible_group", "system", "external"}:
            return "Informe uma origem valida para o documento."

        if data["purpose"] not in {"attachment", "form", "opinion", "evaluation", "generated", "linked_service"}:
            return "Informe uma finalidade valida para o documento."

        if data["form_template_id"] and db.session.get(FormTemplate, data["form_template_id"]) is None:
            return "Formulario associado nao encontrado."

        if data["opinion_template_id"] and db.session.get(OpinionTemplate, data["opinion_template_id"]) is None:
            return "Modelo de parecer associado nao encontrado."

        if data["purpose"] == "linked_service" and not data["linked_service_id"]:
            return "Informe o servico vinculado ao tipo de documento."

        if data["linked_service_id"] and db.session.get(Service, data["linked_service_id"]) is None:
            return "Servico vinculado nao encontrado."

        return None

    def _name_exists(self, name: str, ignore_document_type_id: int | None = None) -> bool:
        query = DocumentType.query.filter(DocumentType.name.ilike(name.strip()))

        if ignore_document_type_id is not None:
            query = query.filter(DocumentType.id != ignore_document_type_id)

        return db.session.query(query.exists()).scalar()

    def _code_exists(self, code: str, ignore_document_type_id: int | None = None) -> bool:
        query = DocumentType.query.filter(DocumentType.code == code.strip())

        if ignore_document_type_id is not None:
            query = query.filter(DocumentType.id != ignore_document_type_id)

        return db.session.query(query.exists()).scalar()

    def _to_dict(self, document_type: DocumentType) -> dict:
        return {
            "id": document_type.id,
            "name": document_type.name,
            "code": document_type.code,
            "description": document_type.description,
            "origin": document_type.origin,
            "purpose": document_type.purpose,
            "module_slug": document_type.module_slug,
            "form_template_id": document_type.form_template_id,
            "form_template_name": document_type.form_template.name if document_type.form_template else "",
            "opinion_template_id": document_type.opinion_template_id,
            "opinion_template_name": (
                document_type.opinion_template.name if document_type.opinion_template else ""
            ),
            "linked_service_id": document_type.linked_service_id,
            "linked_service_name": document_type.linked_service.name if document_type.linked_service else "",
            "linked_service_slug": document_type.linked_service.slug if document_type.linked_service else "",
            "linked_service_module_key": document_type.linked_service.module_key if document_type.linked_service else "",
            "linked_service_required_status": document_type.linked_service_required_status,
            "allowed_formats": document_type.allowed_formats,
            "required_by_default": document_type.required_by_default,
            "allow_multiple_files": document_type.allow_multiple_files,
            "active": document_type.active,
        }

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFD", value.lower())
        ascii_value = "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
        return re.sub(r"-+", "-", slug)

    def _optional_int(self, value) -> int | None:
        return int(value) if value else None


document_types_repository = DocumentTypesRepository()
