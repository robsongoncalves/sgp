from __future__ import annotations

import re
import unicodedata

from app.extensions import db
from app.models import FormTemplate
from app.repositories.utils import bool_value


class FormTemplatesRepository:
    def list(self) -> list[dict]:
        templates = FormTemplate.query.order_by(FormTemplate.name.asc()).all()
        return [self._to_dict(template) for template in templates]

    def get(self, template_id: int) -> FormTemplate | None:
        return db.session.get(FormTemplate, template_id)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        if self._name_exists(normalized_data["name"]):
            return None, "Ja existe um formulario cadastrado com este nome."

        if self._slug_exists(normalized_data["slug"]):
            return None, "Ja existe um formulario cadastrado com este slug."

        template = FormTemplate(**normalized_data)
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
            return None, "Formulario nao encontrado."

        if self._name_exists(normalized_data["name"], ignore_template_id=template_id):
            return None, "Ja existe um formulario cadastrado com este nome."

        if self._slug_exists(normalized_data["slug"], ignore_template_id=template_id):
            return None, "Ja existe um formulario cadastrado com este slug."

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
        fields_schema = data.get("fields_schema", [])

        return {
            "name": name,
            "slug": self._slugify(slug),
            "description": str(data.get("description", "")).strip(),
            "execution_mode": str(data.get("execution_mode", "dynamic")).strip() or "dynamic",
            "fields_schema": fields_schema if isinstance(fields_schema, list) else [],
            "active": bool_value(data.get("active", True)),
        }

    def _validate(self, data: dict) -> str | None:
        if not data["name"]:
            return "Informe o nome do formulario."

        if not data["slug"]:
            return "Informe o slug do formulario."

        if data["execution_mode"] not in {"dynamic", "custom"}:
            return "Informe um modo de execucao valido para o formulario."

        return None

    def _name_exists(self, name: str, ignore_template_id: int | None = None) -> bool:
        query = FormTemplate.query.filter(FormTemplate.name.ilike(name.strip()))
        if ignore_template_id is not None:
            query = query.filter(FormTemplate.id != ignore_template_id)
        return db.session.query(query.exists()).scalar()

    def _slug_exists(self, slug: str, ignore_template_id: int | None = None) -> bool:
        query = FormTemplate.query.filter(FormTemplate.slug == slug.strip())
        if ignore_template_id is not None:
            query = query.filter(FormTemplate.id != ignore_template_id)
        return db.session.query(query.exists()).scalar()

    def _to_dict(self, template: FormTemplate) -> dict:
        return {
            "id": template.id,
            "name": template.name,
            "slug": template.slug,
            "description": template.description,
            "execution_mode": template.execution_mode,
            "fields_schema": template.fields_schema,
            "active": template.active,
        }

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFD", value.lower())
        ascii_value = "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
        return re.sub(r"-+", "-", slug)


form_templates_repository = FormTemplatesRepository()
