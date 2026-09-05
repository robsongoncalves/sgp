from __future__ import annotations

from app.extensions import db
from app.models import ServiceCategory
from app.repositories.utils import bool_value


class ServiceCategoriesRepository:
    def list(self) -> list[dict]:
        categories = ServiceCategory.query.order_by(
            ServiceCategory.display_order.asc(),
            ServiceCategory.name.asc(),
        ).all()
        return [self._to_dict(category) for category in categories]

    def get(self, category_id: int) -> ServiceCategory | None:
        return db.session.get(ServiceCategory, category_id)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data)
        if error:
            return None, error

        name = str(data["name"]).strip()
        if self._name_exists(name):
            return None, "Ja existe uma categoria cadastrada com este nome."

        category = ServiceCategory(
            name=name,
            description=str(data.get("description", "")).strip(),
            display_order=self._parse_display_order(data),
            active=bool_value(data.get("active", True)),
        )
        db.session.add(category)
        db.session.commit()

        return self._to_dict(category), None

    def update(self, category_id: int, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data)
        if error:
            return None, error

        category = self.get(category_id)

        if category is None:
            return None, "Categoria nao encontrada."

        name = str(data["name"]).strip()
        if self._name_exists(name, ignore_category_id=category_id):
            return None, "Ja existe uma categoria cadastrada com este nome."

        category.name = name
        category.description = str(data.get("description", "")).strip()
        category.display_order = self._parse_display_order(data)
        category.active = bool_value(data.get("active", True))
        db.session.commit()

        return self._to_dict(category), None

    def delete(self, category_id: int) -> bool:
        category = self.get(category_id)

        if category is None:
            return False

        db.session.delete(category)
        db.session.commit()
        return True

    def _validate(self, data: dict) -> str | None:
        name = str(data.get("name", "")).strip()

        if not name:
            return "Informe o nome da categoria."

        try:
            display_order = self._parse_display_order(data)
        except ValueError:
            return "Informe uma ordem de exibicao valida."

        if display_order < 0:
            return "A ordem de exibicao nao pode ser negativa."

        return None

    def _name_exists(self, name: str, ignore_category_id: int | None = None) -> bool:
        query = ServiceCategory.query.filter(ServiceCategory.name.ilike(name.strip()))

        if ignore_category_id is not None:
            query = query.filter(ServiceCategory.id != ignore_category_id)

        return db.session.query(query.exists()).scalar()

    def _to_dict(self, category: ServiceCategory) -> dict:
        return {
            "id": category.id,
            "name": category.name,
            "description": category.description,
            "display_order": category.display_order,
            "active": category.active,
        }

    def _parse_display_order(self, data: dict) -> int:
        return int(data.get("display_order", 0))


service_categories_repository = ServiceCategoriesRepository()
