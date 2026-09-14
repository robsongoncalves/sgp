from __future__ import annotations

import re
from datetime import datetime

from app.extensions import db
from app.models import AutomationFunction, DocumentType, Service, ServiceCategory, ServiceHook, ServiceSituation, UserGroup
from app.repositories.utils import bool_value, date_to_api, optional_int


class ServicesRepository:
    def list(self) -> list[dict]:
        services = Service.query.order_by(Service.name.asc()).all()
        return [self._to_dict(service) for service in services]

    def list_public(self) -> list[dict]:
        services = Service.query.filter(Service.active.is_(True)).order_by(
            Service.featured.desc(),
            Service.name.asc(),
        ).all()
        return [self._to_public_dict(service) for service in services]

    def get(self, service_id: int) -> Service | None:
        return db.session.get(Service, service_id)

    def get_by_slug(self, slug: str) -> Service | None:
        return Service.query.filter(Service.slug == slug).first()

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize_payload(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        if self._slug_exists(normalized_data["slug"]):
            return None, "Ja existe um servico cadastrado com este slug."

        service = Service(
            name=normalized_data["name"],
            slug=normalized_data["slug"],
            description=normalized_data["description"],
            documentation_url=normalized_data["documentation_url"],
            implementation_mode=normalized_data["implementation_mode"],
            module_key=normalized_data["module_key"],
            active=normalized_data["active"],
            featured=normalized_data["featured"],
        )
        self._sync_categories(service, normalized_data["category_ids"])
        self._sync_groups(service, normalized_data["group_ids"])
        db.session.add(service)
        db.session.flush()
        self._sync_situations(service, normalized_data["situations"])
        self._sync_hooks(service, normalized_data["hooks"])
        db.session.commit()

        return self._to_dict(service), None

    def update(self, service_id: int, data: dict) -> tuple[dict | None, str | None]:
        normalized_data = self._normalize_payload(data)
        error = self._validate(normalized_data)
        if error:
            return None, error

        service = self.get(service_id)

        if service is None:
            return None, "Servico nao encontrado."

        if self._slug_exists(normalized_data["slug"], ignore_service_id=service_id):
            return None, "Ja existe um servico cadastrado com este slug."

        service.name = normalized_data["name"]
        service.slug = normalized_data["slug"]
        service.description = normalized_data["description"]
        service.documentation_url = normalized_data["documentation_url"]
        service.implementation_mode = normalized_data["implementation_mode"]
        service.module_key = normalized_data["module_key"]
        service.active = normalized_data["active"]
        service.featured = normalized_data["featured"]
        service.updated_at = datetime.utcnow()
        self._sync_categories(service, normalized_data["category_ids"])
        self._sync_groups(service, normalized_data["group_ids"])
        self._sync_situations(service, normalized_data["situations"])
        self._sync_hooks(service, normalized_data["hooks"])
        db.session.commit()

        return self._to_dict(service), None

    def delete(self, service_id: int) -> bool:
        service = self.get(service_id)

        if service is None:
            return False

        db.session.delete(service)
        db.session.commit()
        return True

    def _normalize_payload(self, data: dict) -> dict:
        name = str(data.get("name", "")).strip()
        slug = str(data.get("slug", "")).strip().lower() or self._slugify(name)
        description = data.get("description", "")
        documentation_url = data.get("documentation_url", data.get("documentationUrl", ""))
        situations = [
            {
                "id": optional_int(item.get("id")) or index + 1,
                "name": str(item.get("name", "")).strip(),
                "previous_situation_id": optional_int(item.get("previous_situation_id")),
                "responsible_group_id": optional_int(item.get("responsible_group_id")),
                "is_initial": bool_value(item.get("is_initial", False)),
                "is_final": bool_value(item.get("is_final", False)),
                "requires_opinion": bool_value(item.get("requires_opinion", False)),
                "requires_attachment": bool_value(item.get("requires_attachment", False)),
                "document_type_ids": sorted(set(self._int_list(item.get("document_type_ids", [])))),
                "display_order": int(item.get("display_order") or index + 1),
            }
            for index, item in enumerate(data.get("situations", []))
        ]
        hooks = [
            {
                "id": optional_int(item.get("id")) or index + 1,
                "function_id": optional_int(item.get("function_id")),
                "event_name": str(item.get("event_name", "")).strip(),
                "handler_key": str(item.get("handler_key", "")).strip(),
                "config": item.get("config", {}),
                "execution_order": int(item.get("execution_order") or index + 1),
                "active": bool_value(item.get("active", True)),
            }
            for index, item in enumerate(data.get("hooks", []))
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
            "active": bool_value(data.get("active", True)),
            "featured": bool_value(data.get("featured", False)),
            "category_ids": sorted(set(self._int_list(data.get("category_ids", [])))),
            "group_ids": sorted(set(self._int_list(data.get("group_ids", [])))),
            "situations": situations,
            "hooks": hooks,
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

        situation_names = [situation["name"] for situation in data["situations"]]
        if any(not name for name in situation_names):
            return "Informe o nome de todas as situacoes."

        if len(situation_names) != len(set(name.lower() for name in situation_names)):
            return "Nao repita nomes de situacoes no mesmo servico."

        initial_count = sum(1 for situation in data["situations"] if situation["is_initial"])
        if data["situations"] and initial_count != 1:
            return "Informe exatamente uma situacao inicial."

        valid_situation_ids = {situation["id"] for situation in data["situations"]}
        for situation in data["situations"]:
            if (
                situation["previous_situation_id"] is not None
                and situation["previous_situation_id"] not in valid_situation_ids
            ):
                return "A situacao anterior informada nao existe neste servico."

        for hook in data["hooks"]:
            if not hook["event_name"]:
                return "Informe o evento de todas as automacoes."

            if hook["function_id"] and db.session.get(AutomationFunction, hook["function_id"]) is None:
                return "Function associada nao encontrada."

            if not hook["function_id"] and not hook["handler_key"]:
                return "Informe a function ou handler de todas as automacoes."

            if not isinstance(hook["config"], dict):
                return "A configuracao da automacao deve ser um objeto JSON."

        return None

    def _sync_categories(self, service: Service, category_ids: list[int]) -> None:
        service.categories = ServiceCategory.query.filter(
            ServiceCategory.id.in_(category_ids)
        ).all() if category_ids else []

    def _sync_groups(self, service: Service, group_ids: list[int]) -> None:
        service.groups = UserGroup.query.filter(UserGroup.id.in_(group_ids)).all() if group_ids else []

    def _sync_situations(self, service: Service, situations_data: list[dict]) -> None:
        current_by_id = {situation.id: situation for situation in service.situations}
        incoming_ids = {
            situation["id"]
            for situation in situations_data
            if situation["id"] in current_by_id
        }

        for situation in list(service.situations):
            if situation.id not in incoming_ids:
                db.session.delete(situation)

        db.session.flush()

        situation_by_input_id: dict[int, ServiceSituation] = {}
        for situation_data in situations_data:
            situation = current_by_id.get(situation_data["id"])

            if situation is None:
                situation = ServiceSituation(service_id=service.id)
                db.session.add(situation)

            situation.name = situation_data["name"]
            situation.previous_situation_id = None
            situation.responsible_group_id = situation_data["responsible_group_id"]
            situation.is_initial = situation_data["is_initial"]
            situation.is_final = situation_data["is_final"]
            situation.requires_opinion = situation_data["requires_opinion"]
            situation.requires_attachment = situation_data["requires_attachment"]
            situation.display_order = situation_data["display_order"]
            situation.document_types = DocumentType.query.filter(
                DocumentType.id.in_(situation_data["document_type_ids"])
            ).all() if situation_data["document_type_ids"] else []
            situation_by_input_id[situation_data["id"]] = situation

        db.session.flush()

        for situation_data in situations_data:
            previous_input_id = situation_data["previous_situation_id"]
            if previous_input_id is None:
                continue

            situation_by_input_id[situation_data["id"]].previous_situation_id = (
                situation_by_input_id[previous_input_id].id
            )

    def _sync_hooks(self, service: Service, hooks_data: list[dict]) -> None:
        current_by_id = {hook.id: hook for hook in service.hooks}
        incoming_ids = {
            hook["id"]
            for hook in hooks_data
            if hook["id"] in current_by_id
        }

        for hook in list(service.hooks):
            if hook.id not in incoming_ids:
                db.session.delete(hook)

        db.session.flush()

        for hook_data in hooks_data:
            hook = current_by_id.get(hook_data["id"])

            if hook is None:
                hook = ServiceHook(service_id=service.id)
                db.session.add(hook)

            hook.function_id = hook_data["function_id"]
            hook.event_name = hook_data["event_name"]
            hook.handler_key = hook_data["handler_key"]
            hook.config = hook_data["config"]
            hook.execution_order = hook_data["execution_order"]
            hook.active = hook_data["active"]

    def _slug_exists(self, slug: str, ignore_service_id: int | None = None) -> bool:
        query = Service.query.filter(Service.slug == slug)

        if ignore_service_id is not None:
            query = query.filter(Service.id != ignore_service_id)

        return db.session.query(query.exists()).scalar()

    def _to_dict(self, service: Service) -> dict:
        situations = sorted(
            service.situations,
            key=lambda situation: (situation.display_order, situation.name.lower()),
        )
        return {
            "id": service.id,
            "name": service.name,
            "slug": service.slug,
            "description": service.description,
            "documentation_url": service.documentation_url,
            "implementation_mode": service.implementation_mode,
            "module_key": service.module_key,
            "active": service.active,
            "featured": service.featured,
            "updated_at": date_to_api(service.updated_at),
            "category_ids": sorted(category.id for category in service.categories),
            "group_ids": sorted(group.id for group in service.groups),
            "situations": [
                {
                    "id": situation.id,
                    "name": situation.name,
                    "previous_situation_id": situation.previous_situation_id,
                    "responsible_group_id": situation.responsible_group_id,
                    "is_initial": situation.is_initial,
                    "is_final": situation.is_final,
                    "requires_opinion": situation.requires_opinion,
                    "requires_attachment": situation.requires_attachment,
                    "document_type_ids": sorted(document_type.id for document_type in situation.document_types),
                    "display_order": situation.display_order,
                }
                for situation in situations
            ],
            "hooks": [
                {
                    "id": hook.id,
                    "function_id": hook.function_id,
                    "function_name": hook.function.name if hook.function else "",
                    "event_name": hook.event_name,
                    "handler_key": hook.handler_key,
                    "config": hook.config or {},
                    "execution_order": hook.execution_order,
                    "active": hook.active,
                }
                for hook in service.hooks
            ],
        }

    def _to_public_dict(self, service: Service) -> dict:
        categories = sorted(
            (category for category in service.categories if category.active),
            key=lambda category: (category.display_order, category.name.lower()),
        )
        return {
            "id": service.id,
            "name": service.name,
            "slug": service.slug,
            "description": service.description,
            "documentation_url": service.documentation_url,
            "featured": service.featured,
            "updated_at": date_to_api(service.updated_at),
            "categories": [
                {
                    "id": category.id,
                    "name": category.name,
                    "description": category.description,
                    "display_order": category.display_order,
                }
                for category in categories
            ],
        }

    def _int_list(self, value: list) -> list[int]:
        return [int(item) for item in value if str(item).strip()]

    def _slugify(self, value: str) -> str:
        slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
        return re.sub(r"-+", "-", slug)


services_repository = ServicesRepository()
