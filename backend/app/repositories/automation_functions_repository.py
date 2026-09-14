from __future__ import annotations

import re
import unicodedata

from app.extensions import db
from app.models import AutomationFunction
from app.repositories.utils import bool_value


class AutomationFunctionsRepository:
    def list(self) -> list[dict]:
        functions = AutomationFunction.query.order_by(AutomationFunction.name.asc()).all()
        return [self._to_dict(function) for function in functions]

    def get(self, function_id: int) -> AutomationFunction | None:
        return db.session.get(AutomationFunction, function_id)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        if self._name_exists(normalized_data["name"]):
            return None, "Ja existe uma function cadastrada com este nome."

        if self._slug_exists(normalized_data["slug"]):
            return None, "Ja existe uma function cadastrada com esta chave."

        function = AutomationFunction(**normalized_data)
        db.session.add(function)
        db.session.commit()

        return self._to_dict(function), None

    def update(self, function_id: int, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        function = self.get(function_id)
        if function is None:
            return None, "Function nao encontrada."

        if self._name_exists(normalized_data["name"], ignore_function_id=function_id):
            return None, "Ja existe uma function cadastrada com este nome."

        if self._slug_exists(normalized_data["slug"], ignore_function_id=function_id):
            return None, "Ja existe uma function cadastrada com esta chave."

        for field, value in normalized_data.items():
            setattr(function, field, value)

        db.session.commit()

        return self._to_dict(function), None

    def delete(self, function_id: int) -> bool:
        function = self.get(function_id)
        if function is None:
            return False

        db.session.delete(function)
        db.session.commit()
        return True

    def _normalize(self, data: dict) -> dict:
        name = str(data.get("name", "")).strip()
        slug = str(data.get("slug", "")).strip() or self._slugify(name)
        timeout_seconds = int(data.get("timeout_seconds") or 10)

        return {
            "name": name,
            "slug": self._slugify(slug),
            "description": str(data.get("description", "")).strip(),
            "language": str(data.get("language", "python")).strip().lower() or "python",
            "source_code": str(data.get("source_code", "")).strip(),
            "timeout_seconds": max(timeout_seconds, 1),
            "active": bool_value(data.get("active", True)),
        }

    def _validate(self, data: dict) -> str | None:
        if not data["name"]:
            return "Informe o nome da function."

        if not data["slug"]:
            return "Informe a chave da function."

        if data["language"] != "python":
            return "Somente functions Python sao suportadas nesta versao."

        if not data["source_code"]:
            return "Informe o codigo Python da function."

        if "def handle(" not in data["source_code"]:
            return "A function deve declarar def handle(context)."

        return None

    def _name_exists(self, name: str, ignore_function_id: int | None = None) -> bool:
        query = AutomationFunction.query.filter(AutomationFunction.name.ilike(name.strip()))

        if ignore_function_id is not None:
            query = query.filter(AutomationFunction.id != ignore_function_id)

        return db.session.query(query.exists()).scalar()

    def _slug_exists(self, slug: str, ignore_function_id: int | None = None) -> bool:
        query = AutomationFunction.query.filter(AutomationFunction.slug == slug.strip())

        if ignore_function_id is not None:
            query = query.filter(AutomationFunction.id != ignore_function_id)

        return db.session.query(query.exists()).scalar()

    def _to_dict(self, function: AutomationFunction) -> dict:
        return {
            "id": function.id,
            "name": function.name,
            "slug": function.slug,
            "description": function.description,
            "language": function.language,
            "source_code": function.source_code,
            "timeout_seconds": function.timeout_seconds,
            "active": function.active,
        }

    def _slugify(self, value: str) -> str:
        normalized = unicodedata.normalize("NFD", value.lower())
        ascii_value = "".join(
            char for char in normalized if unicodedata.category(char) != "Mn"
        )
        slug = re.sub(r"[^a-z0-9]+", "-", ascii_value).strip("-")
        return re.sub(r"-+", "-", slug)


automation_functions_repository = AutomationFunctionsRepository()
