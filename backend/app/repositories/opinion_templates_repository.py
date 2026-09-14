from __future__ import annotations

import re
import unicodedata

from app.extensions import db
from app.models import OpinionTemplate, UserGroup
from app.repositories.utils import bool_value


class OpinionTemplatesRepository:
    def list(self) -> list[dict]:
        templates = OpinionTemplate.query.order_by(OpinionTemplate.name.asc()).all()
        return [self._to_dict(template) for template in templates]

    def get(self, template_id: int) -> OpinionTemplate | None:
        return db.session.get(OpinionTemplate, template_id)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        if self._name_exists(normalized_data["name"]):
            return None, "Ja existe um modelo de parecer cadastrado com este nome."

        if self._slug_exists(normalized_data["slug"]):
            return None, "Ja existe um modelo de parecer cadastrado com este slug."

        template = OpinionTemplate(**normalized_data)
        db.session.add(template)
        db.session.commit()

        return self._to_dict(template), None

    def update(self, template_id: int, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        template = self.get(template_id)
        if template is None:
            return None, "Modelo de parecer nao encontrado."

        if self._name_exists(normalized_data["name"], ignore_template_id=template_id):
            return None, "Ja existe um modelo de parecer cadastrado com este nome."

        if self._slug_exists(normalized_data["slug"], ignore_template_id=template_id):
            return None, "Ja existe um modelo de parecer cadastrado com este slug."

        for field, value in normalized_data.items():
            setattr(template, field, value)

        db.session.commit()
        return self._to_dict(template), None

    def delete(self, template_id: int) -> bool:
        template = self.get(template_id)
        if template is None:
            return False

        db.session.delete(template)
        db.session.commit()
        return True

    def _normalize(self, data: dict) -> dict:
        name = str(data.get("name", "")).strip()
        slug = str(data.get("slug", "")).strip() or self._slugify(name)
        decision_options = data.get("decision_options", [])
        fields_schema = data.get("fields_schema", [])
        group_id = data.get("default_responsible_group_id")

        return {
            "name": name,
            "slug": self._slugify(slug),
            "description": str(data.get("description", "")).strip(),
            "execution_mode": str(data.get("execution_mode", "dynamic")).strip() or "dynamic",
            "default_responsible_group_id": int(group_id) if group_id else None,
            "decision_options": decision_options if isinstance(decision_options, list) else [],
            "fields_schema": fields_schema if isinstance(fields_schema, list) else [],
            "requires_justification": bool_value(data.get("requires_justification", True)),
            "requires_signature": bool_value(data.get("requires_signature", True)),
            "allow_attachments": bool_value(data.get("allow_attachments", True)),
            "active": bool_value(data.get("active", True)),
        }

    def _validate(self, data: dict) -> str | None:
        if not data["name"]:
            return "Informe o nome do modelo de parecer."

        if not data["slug"]:
            return "Informe o slug do modelo de parecer."

        if data["execution_mode"] not in {"dynamic", "custom"}:
            return "Informe um modo de execucao valido para o parecer."

        group_id = data["default_responsible_group_id"]
        if group_id and db.session.get(UserGroup, group_id) is None:
            return "Unidade responsavel padrao nao encontrada."

        return None

    def _name_exists(self, name: str, ignore_template_id: int | None = None) -> bool:
        query = OpinionTemplate.query.filter(OpinionTemplate.name.ilike(name.strip()))
        if ignore_template_id is not None:
            query = query.filter(OpinionTemplate.id != ignore_template_id)
        return db.session.query(query.exists()).scalar()

    def _slug_exists(self, slug: str, ignore_template_id: int | None = None) -> bool:
        query = OpinionTemplate.query.filter(OpinionTemplate.slug == slug.strip())
        if ignore_template_id is not None:
            query = query.filter(OpinionTemplate.id != ignore_template_id)
        return db.session.query(query.exists()).scalar()

    def _to_dict(self, template: OpinionTemplate) -> dict:
        group = template.default_responsible_group

        return {
            "id": template.id,
            "name": template.name,
            "slug": template.slug,
            "description": template.description,
            "execution_mode": template.execution_mode,
            "default_responsible_group_id": template.default_responsible_group_id,
            "default_responsible_group_name": group.name if group else "",
            "decision_options": template.decision_options,
            "fields_schema": template.fields_schema,
            "requires_justification": template.requires_justification,
            "requires_signature": template.requires_signature,
            "allow_attachments": template.allow_attachments,
            "active": template.active,
        }

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFD", value.lower())
        ascii_value = "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
        return re.sub(r"-+", "-", slug)


opinion_templates_repository = OpinionTemplatesRepository()
