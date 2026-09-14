from __future__ import annotations

from app.extensions import db
from app.models import ServiceCategory
from app.repositories.utils import bool_value, optional_int


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
            parent_category_id=self._parent_category_id(data),
            display_order=self._parse_display_order(data),
            show_on_main_menu=bool_value(data.get("show_on_main_menu", False)),
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

        parent_category_id = self._parent_category_id(data)
        hierarchy_error = self._validate_hierarchy(category, parent_category_id)
        if hierarchy_error:
            return None, hierarchy_error

        category.name = name
        category.description = str(data.get("description", "")).strip()
        category.parent_category_id = parent_category_id
        category.display_order = self._parse_display_order(data)
        category.show_on_main_menu = bool_value(data.get("show_on_main_menu", False))
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

        parent_category_id = self._parent_category_id(data)
        if parent_category_id is not None and db.session.get(ServiceCategory, parent_category_id) is None:
            return "Categoria pai nao encontrada."

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
            "parent_category_id": category.parent_category_id,
            "parent_category_name": category.parent.name if category.parent else "",
            "display_order": category.display_order,
            "show_on_main_menu": category.show_on_main_menu,
            "active": category.active,
        }

    def _parse_display_order(self, data: dict) -> int:
        return int(data.get("display_order", 0))

    def _parent_category_id(self, data: dict) -> int | None:
        return optional_int(data.get("parent_category_id"))

    def _validate_hierarchy(
        self,
        category: ServiceCategory,
        parent_category_id: int | None,
    ) -> str | None:
        if parent_category_id is None:
            return None

        if parent_category_id == category.id:
            return "Uma categoria nao pode ser filha dela mesma."

        current = db.session.get(ServiceCategory, parent_category_id)
        visited_category_ids: set[int] = set()

        while current is not None:
            if current.id == category.id:
                return "Hierarquia invalida: a categoria pai escolhida criaria um ciclo."

            if current.id in visited_category_ids:
                return "Hierarquia invalida: foi detectado um ciclo entre categorias."

            visited_category_ids.add(current.id)
            current = current.parent


service_categories_repository = ServiceCategoriesRepository()
