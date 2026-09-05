from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date
import json
from pathlib import Path
import re
from threading import Lock

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "services.json"


@dataclass
class ServiceSituation:
    id: int
    name: str
    previous_situation_id: int | None = None
    responsible_group_id: int | None = None
    is_initial: bool = False
    is_final: bool = False
    requires_opinion: bool = False
    requires_attachment: bool = False
    display_order: int = 0


@dataclass
class Service:
    id: int
    name: str
    slug: str
    description: str = ""
    documentation_url: str = ""
    implementation_mode: str = "custom_module"
    module_key: str = ""
    active: bool = True
    featured: bool = False
    updated_at: str = ""
    category_ids: list[int] = field(default_factory=list)
    group_ids: list[int] = field(default_factory=list)
    situations: list[ServiceSituation] = field(default_factory=list)


class ServicesRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._ensure_data_file()

    def list(self) -> list[dict]:
        services = sorted(
            self._read_services(),
            key=lambda service: service.name.lower(),
        )
        return [self._to_dict(service) for service in services]

    def get(self, service_id: int) -> Service | None:
        return next(
            (
                service
                for service in self._read_services()
                if service.id == service_id
            ),
            None,
        )

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize_payload(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        with self._lock:
            services = self._read_services()

            if self._slug_exists(normalized_data["slug"], services=services):
                return None, "Ja existe um servico cadastrado com este slug."

            service = Service(
                id=self._next_id(services),
                **normalized_data,
            )
            services.append(service)
            self._write_services(services)

        return self._to_dict(service), None

    def update(self, service_id: int, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize_payload(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        with self._lock:
            services = self._read_services()
            service = next(
                (item for item in services if item.id == service_id),
                None,
            )

            if service is None:
                return None, "Servico nao encontrado."

            if self._slug_exists(
                normalized_data["slug"],
                ignore_service_id=service_id,
                services=services,
            ):
                return None, "Ja existe um servico cadastrado com este slug."

            service.name = normalized_data["name"]
            service.slug = normalized_data["slug"]
            service.description = normalized_data["description"]
            service.documentation_url = normalized_data["documentation_url"]
            service.implementation_mode = normalized_data["implementation_mode"]
            service.module_key = normalized_data["module_key"]
            service.active = normalized_data["active"]
            service.featured = normalized_data["featured"]
            service.updated_at = date.today().isoformat()
            service.category_ids = normalized_data["category_ids"]
            service.group_ids = normalized_data["group_ids"]
            service.situations = normalized_data["situations"]
            self._write_services(services)

        return self._to_dict(service), None

    def delete(self, service_id: int) -> bool:
        with self._lock:
            services = self._read_services()
            service = next(
                (item for item in services if item.id == service_id),
                None,
            )

            if service is None:
                return False

            services.remove(service)
            self._write_services(services)
            return True

    def _normalize_payload(self, data: dict) -> dict:
        name = str(data.get("name", "")).strip()
        slug = str(data.get("slug", "")).strip().lower() or self._slugify(name)
        description = data.get("description", "")
        documentation_url = data.get("documentation_url", data.get("documentationUrl", ""))
        situations = [
            ServiceSituation(
                id=int(item.get("id") or index + 1),
                name=str(item.get("name", "")).strip(),
                previous_situation_id=self._optional_int(item.get("previous_situation_id")),
                responsible_group_id=self._optional_int(item.get("responsible_group_id")),
                is_initial=bool(item.get("is_initial", False)),
                is_final=bool(item.get("is_final", False)),
                requires_opinion=bool(item.get("requires_opinion", False)),
                requires_attachment=bool(item.get("requires_attachment", False)),
                display_order=int(item.get("display_order") or index + 1),
            )
            for index, item in enumerate(data.get("situations", []))
        ]

        return {
            "name": name,
            "slug": self._slugify(slug),
            "description": str(description or "").strip(),
            "documentation_url": str(documentation_url or "").strip(),
            "implementation_mode": str(
                data.get("implementation_mode", "custom_module")
            ).strip() or "custom_module",
            "module_key": str(data.get("module_key", "")).strip(),
            "active": self._bool_value(data.get("active", True)),
            "featured": self._bool_value(data.get("featured", False)),
            "updated_at": str(data.get("updated_at") or date.today().isoformat()).strip(),
            "category_ids": sorted(set(self._int_list(data.get("category_ids", [])))),
            "group_ids": sorted(set(self._int_list(data.get("group_ids", [])))),
            "situations": situations,
        }

    def _validate(self, data: dict) -> str | None:
        if not data["name"]:
            return "Informe o nome do servico."

        if not data["slug"]:
            return "Informe o slug do servico."

        if data["implementation_mode"] not in {"custom_module", "standard"}:
            return "Informe um modo de implementacao valido."

        if data["implementation_mode"] == "custom_module" and not data["module_key"]:
            return "Informe a chave do modulo especifico."

        situation_names = [situation.name for situation in data["situations"]]
        if any(not name for name in situation_names):
            return "Informe o nome de todas as situacoes."

        if len(situation_names) != len(set(name.lower() for name in situation_names)):
            return "Nao repita nomes de situacoes no mesmo servico."

        initial_count = sum(1 for situation in data["situations"] if situation.is_initial)
        if data["situations"] and initial_count != 1:
            return "Informe exatamente uma situacao inicial."

        valid_situation_ids = {situation.id for situation in data["situations"]}
        for situation in data["situations"]:
            if (
                situation.previous_situation_id is not None
                and situation.previous_situation_id not in valid_situation_ids
            ):
                return "A situacao anterior informada nao existe neste servico."

        return None

    def _slug_exists(
        self,
        slug: str,
        services: list[Service],
        ignore_service_id: int | None = None,
    ) -> bool:
        return any(
            service.slug == slug and service.id != ignore_service_id
            for service in services
        )

    def _read_services(self) -> list[Service]:
        with DATA_FILE.open(encoding="utf-8") as file:
            data = json.load(file)

        return [
            Service(
                id=item["id"],
                name=item["name"],
                slug=item["slug"],
                description=item.get("description", ""),
                documentation_url=item.get("documentation_url", ""),
                implementation_mode=item.get("implementation_mode", "custom_module"),
                module_key=item.get("module_key", ""),
                active=item.get("active", True),
                featured=item.get("featured", False),
                updated_at=item.get("updated_at", date.today().isoformat()),
                category_ids=self._int_list(item.get("category_ids", [])),
                group_ids=self._int_list(item.get("group_ids", [])),
                situations=[
                    ServiceSituation(
                        id=situation["id"],
                        name=situation["name"],
                        previous_situation_id=self._optional_int(
                            situation.get("previous_situation_id")
                        ),
                        responsible_group_id=self._optional_int(
                            situation.get("responsible_group_id")
                        ),
                        is_initial=situation.get("is_initial", False),
                        is_final=situation.get("is_final", False),
                        requires_opinion=situation.get("requires_opinion", False),
                        requires_attachment=situation.get("requires_attachment", False),
                        display_order=situation.get("display_order", 0),
                    )
                    for situation in item.get("situations", [])
                ],
            )
            for item in data
        ]

    def _write_services(self, services: list[Service]) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                [self._to_dict(service) for service in services],
                file,
                ensure_ascii=True,
                indent=2,
            )
            file.write("\n")

    def _to_dict(self, service: Service) -> dict:
        data = asdict(service)
        data["situations"] = [
            asdict(situation)
            for situation in sorted(
                service.situations,
                key=lambda situation: (situation.display_order, situation.name.lower()),
            )
        ]
        return data

    def _ensure_data_file(self) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not DATA_FILE.exists():
            self._write_services([])

    def _next_id(self, services: list[Service]) -> int:
        if not services:
            return 1

        return max(service.id for service in services) + 1

    def _int_list(self, value: list) -> list[int]:
        return [int(item) for item in value if str(item).strip()]

    def _optional_int(self, value) -> int | None:
        if value in (None, ""):
            return None

        return int(value)

    def _bool_value(self, value) -> bool:
        if isinstance(value, bool):
            return value

        if isinstance(value, str):
            return value.strip().lower() in {"1", "true", "sim", "yes", "on"}

        return bool(value)

    def _slugify(self, value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return re.sub(r"-+", "-", slug)


services_repository = ServicesRepository()
