from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from threading import Lock

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "service_categories.json"


@dataclass
class ServiceCategory:
    id: int
    name: str
    description: str = ""
    display_order: int = 0
    active: bool = True


class ServiceCategoriesRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._ensure_data_file()

    def list(self) -> list[dict]:
        categories = sorted(
            self._read_categories(),
            key=lambda category: (category.display_order, category.name.lower()),
        )
        return [asdict(category) for category in categories]

    def get(self, category_id: int) -> ServiceCategory | None:
        return next(
            (category for category in self._read_categories() if category.id == category_id),
            None,
        )

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data)
        if error:
            return None, error

        with self._lock:
            categories = self._read_categories()

            if self._name_exists(data["name"], categories=categories):
                return None, "Ja existe uma categoria cadastrada com este nome."

            category = ServiceCategory(
                id=self._next_id(categories),
                name=data["name"].strip(),
                description=str(data.get("description", "")).strip(),
                display_order=self._parse_display_order(data),
                active=bool(data.get("active", True)),
            )
            categories.append(category)
            self._write_categories(categories)

        return asdict(category), None

    def update(self, category_id: int, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data)
        if error:
            return None, error

        with self._lock:
            categories = self._read_categories()
            category = next((item for item in categories if item.id == category_id), None)

            if category is None:
                return None, "Categoria nao encontrada."

            if self._name_exists(
                data["name"],
                ignore_category_id=category_id,
                categories=categories,
            ):
                return None, "Ja existe uma categoria cadastrada com este nome."

            category.name = data["name"].strip()
            category.description = str(data.get("description", "")).strip()
            category.display_order = self._parse_display_order(data)
            category.active = bool(data.get("active", True))
            self._write_categories(categories)

        return asdict(category), None

    def delete(self, category_id: int) -> bool:
        with self._lock:
            categories = self._read_categories()
            category = next((item for item in categories if item.id == category_id), None)

            if category is None:
                return False

            categories.remove(category)
            self._write_categories(categories)
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

    def _name_exists(
        self,
        name: str,
        categories: list[ServiceCategory],
        ignore_category_id: int | None = None,
    ) -> bool:
        normalized_name = name.strip().lower()
        return any(
            category.name.lower() == normalized_name and category.id != ignore_category_id
            for category in categories
        )

    def _read_categories(self) -> list[ServiceCategory]:
        with DATA_FILE.open(encoding="utf-8") as file:
            data = json.load(file)

        return [
            ServiceCategory(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                display_order=int(item.get("display_order", 0)),
                active=item.get("active", True),
            )
            for item in data
        ]

    def _write_categories(self, categories: list[ServiceCategory]) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                [asdict(category) for category in categories],
                file,
                ensure_ascii=True,
                indent=2,
            )
            file.write("\n")

    def _ensure_data_file(self) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not DATA_FILE.exists():
            self._write_categories([])

    def _next_id(self, categories: list[ServiceCategory]) -> int:
        if not categories:
            return 1

        return max(category.id for category in categories) + 1

    def _parse_display_order(self, data: dict) -> int:
        return int(data.get("display_order", 0))


service_categories_repository = ServiceCategoriesRepository()
