from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path

import click
from sqlalchemy import text

from app.extensions import db
from app.models import (
    DocumentType,
    FormTemplate,
    OpinionTemplate,
    Service,
    ServiceCategory,
    ServiceRequest,
    ServiceRequestAttachment,
    ServiceRequestDocument,
    ServiceRequestMovement,
    ServiceSituation,
    User,
    UserGroup,
    service_category_association,
    service_group_association,
    service_situation_document_type_association,
    user_group_members,
)

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"


def register_cli(app):
    app.cli.add_command(seed_json_command)
    app.cli.add_command(seed_document_config_command)


@click.command("seed-json")
@click.option("--reset", is_flag=True, help="Remove dados existentes antes de importar.")
def seed_json_command(reset: bool):
    if reset:
        _reset_database()

    _seed_users()
    _seed_user_groups()
    _seed_service_categories()
    _seed_form_templates()
    _seed_opinion_templates()
    _seed_document_types()
    _seed_services()
    _seed_service_requests()
    db.session.commit()

    click.echo("Dados JSON importados para o PostgreSQL.")


@click.command("seed-document-config")
def seed_document_config_command():
    _seed_form_templates()
    _seed_opinion_templates()
    _seed_document_types()
    db.session.commit()

    click.echo("Configuracao documental importada para o PostgreSQL.")


def _reset_database() -> None:
    for table in (
        ServiceRequestMovement.__table__,
        ServiceRequestAttachment.__table__,
        ServiceRequestDocument.__table__,
        ServiceRequest.__table__,
        service_situation_document_type_association,
        ServiceSituation.__table__,
        service_group_association,
        service_category_association,
        user_group_members,
        Service.__table__,
        DocumentType.__table__,
        OpinionTemplate.__table__,
        FormTemplate.__table__,
        ServiceCategory.__table__,
        UserGroup.__table__,
        User.__table__,
    ):
        db.session.execute(table.delete())

    db.session.commit()


def _seed_users() -> None:
    for item in _read_json("users.json"):
        user = db.session.get(User, item["id"]) or User(id=item["id"])
        user.name = item["name"]
        user.email = item["email"]
        user.password_hash = item.get("password_hash", "")
        user.siape = item.get("siape", "")
        user.cargo = item.get("cargo", "")
        user.classe_nivel = item.get("classe_nivel", "")
        user.local_exercicio = item.get("local_exercicio", "")
        user.telefone = item.get("telefone", "")
        user.active = item.get("active", True)
        db.session.add(user)

    db.session.flush()
    _reset_sequence("users", "id")


def _seed_user_groups() -> None:
    for item in _read_json("user_groups.json"):
        group = db.session.get(UserGroup, item["id"]) or UserGroup(id=item["id"])
        group.name = item["name"]
        group.description = item.get("description", "")
        group.manager_user_id = item.get("manager_user_id")
        group.active = item.get("active", True)
        db.session.add(group)

    db.session.flush()
    _reset_sequence("user_groups", "id")

    db.session.execute(user_group_members.delete())
    for membership in _read_json("user_group_members.json"):
        for user_id in membership.get("user_ids", []):
            if db.session.get(User, user_id) and db.session.get(UserGroup, membership["group_id"]):
                db.session.execute(
                    user_group_members.insert().values(
                        user_id=user_id,
                        group_id=membership["group_id"],
                        is_group_admin=False,
                    )
                )


def _seed_service_categories() -> None:
    for item in _read_json("service_categories.json"):
        category = db.session.get(ServiceCategory, item["id"]) or ServiceCategory(id=item["id"])
        category.name = item["name"]
        category.description = item.get("description", "")
        category.display_order = int(item.get("display_order", 0))
        category.active = item.get("active", True)
        db.session.add(category)

    db.session.flush()
    _reset_sequence("service_categories", "id")


def _seed_document_types() -> None:
    for item in _read_json("document_types.json"):
        document_type = db.session.get(DocumentType, item["id"]) or DocumentType(id=item["id"])
        document_type.name = item["name"]
        document_type.code = item["code"]
        document_type.description = item.get("description", "")
        document_type.origin = item.get("origin", "requester")
        document_type.purpose = item.get("purpose", "attachment")
        document_type.module_slug = item.get("module_slug", "")
        document_type.form_template_id = item.get("form_template_id")
        document_type.opinion_template_id = item.get("opinion_template_id")
        document_type.linked_service_id = item.get("linked_service_id")
        document_type.linked_service_required_status = item.get("linked_service_required_status", "")
        document_type.allowed_formats = item.get("allowed_formats", "PDF")
        document_type.required_by_default = item.get("required_by_default", False)
        document_type.allow_multiple_files = item.get("allow_multiple_files", False)
        document_type.active = item.get("active", True)
        db.session.add(document_type)

    db.session.flush()
    _reset_sequence("document_types", "id")


def _seed_form_templates() -> None:
    for item in _read_json("form_templates.json"):
        template = db.session.get(FormTemplate, item["id"]) or FormTemplate(id=item["id"])
        template.name = item["name"]
        template.slug = item["slug"]
        template.description = item.get("description", "")
        template.execution_mode = item.get("execution_mode", "dynamic")
        template.fields_schema = item.get("fields_schema", [])
        template.active = item.get("active", True)
        db.session.add(template)

    db.session.flush()
    _reset_sequence("form_templates", "id")


def _seed_opinion_templates() -> None:
    for item in _read_json("opinion_templates.json"):
        template = db.session.get(OpinionTemplate, item["id"]) or OpinionTemplate(id=item["id"])
        template.name = item["name"]
        template.slug = item["slug"]
        template.description = item.get("description", "")
        template.execution_mode = item.get("execution_mode", "dynamic")
        template.default_responsible_group_id = item.get("default_responsible_group_id")
        template.decision_options = item.get("decision_options", [])
        template.fields_schema = item.get("fields_schema", [])
        template.requires_justification = item.get("requires_justification", True)
        template.requires_signature = item.get("requires_signature", True)
        template.allow_attachments = item.get("allow_attachments", True)
        template.active = item.get("active", True)
        db.session.add(template)

    db.session.flush()
    _reset_sequence("opinion_templates", "id")


def _seed_services() -> None:
    db.session.execute(service_category_association.delete())
    db.session.execute(service_group_association.delete())

    for item in _read_json("services.json"):
        service = db.session.get(Service, item["id"]) or Service(id=item["id"])
        service.name = item["name"]
        service.slug = item["slug"]
        service.description = item.get("description", "")
        service.documentation_url = item.get("documentation_url", "")
        service.implementation_mode = item.get("implementation_mode", "custom_module")
        service.module_key = item.get("module_key", "")
        service.active = item.get("active", True)
        service.featured = item.get("featured", False)
        db.session.add(service)
        db.session.flush()

        service.categories = [
            category
            for category_id in item.get("category_ids", [])
            if (category := db.session.get(ServiceCategory, category_id))
        ]
        service.groups = [
            group
            for group_id in item.get("group_ids", [])
            if (group := db.session.get(UserGroup, group_id))
        ]

        _seed_service_situations(service, item.get("situations", []))

    db.session.flush()
    _reset_sequence("services", "id")
    _reset_sequence("service_situations", "id")


def _seed_service_situations(service: Service, situations_data: list[dict]) -> None:
    for situation in list(service.situations):
        db.session.delete(situation)

    db.session.flush()

    situation_by_json_id = {}
    for item in situations_data:
        situation = ServiceSituation(
            service_id=service.id,
            name=item["name"],
            responsible_group_id=item.get("responsible_group_id"),
            is_initial=item.get("is_initial", False),
            is_final=item.get("is_final", False),
            requires_opinion=item.get("requires_opinion", False),
            requires_attachment=item.get("requires_attachment", False),
            display_order=int(item.get("display_order", 0)),
        )
        db.session.add(situation)
        db.session.flush()
        situation.document_types = [
            document_type
            for document_type_id in item.get("document_type_ids", [])
            if (document_type := db.session.get(DocumentType, document_type_id))
        ]
        situation_by_json_id[item["id"]] = situation

    for item in situations_data:
        previous_json_id = item.get("previous_situation_id")
        if previous_json_id in situation_by_json_id:
            situation_by_json_id[item["id"]].previous_situation_id = situation_by_json_id[previous_json_id].id


def _seed_service_requests() -> None:
    for item in _read_json("service_requests.json"):
        service = db.session.get(Service, item["service_id"])
        requester = db.session.get(User, item.get("requester_user_id", 3))

        if service is None or requester is None:
            continue

        service_request = db.session.get(ServiceRequest, item["id"]) or ServiceRequest(id=item["id"])
        service_request.number = item["number"]
        service_request.service_id = service.id
        service_request.requester_user_id = requester.id
        service_request.current_situation_id = _initial_situation_id(service, item.get("current_situation_name"))
        service_request.status = item.get("status", item.get("current_situation_name", "Solicitado"))
        service_request.form_data = {}
        service_request.created_at = _parse_datetime(item.get("created_at"))
        service_request.updated_at = _parse_datetime(item.get("updated_at"))
        service_request.canceled_at = _parse_datetime(item.get("canceled_at")) if item.get("canceled_at") else None
        db.session.add(service_request)

    db.session.flush()
    _reset_sequence("service_requests", "id")


def _initial_situation_id(service: Service, situation_name: str | None) -> int | None:
    if situation_name:
        for situation in service.situations:
            if situation.name == situation_name:
                return situation.id

    initial = next((situation for situation in service.situations if situation.is_initial), None)
    return initial.id if initial else None


def _parse_datetime(value: str | None) -> datetime:
    if not value:
        return datetime.utcnow().replace(microsecond=0)

    return datetime.fromisoformat(value)


def _read_json(filename: str) -> list[dict]:
    path = DATA_DIR / filename

    if not path.exists():
        return []

    with path.open(encoding="utf-8") as file:
        return json.load(file)


def _reset_sequence(table_name: str, column_name: str) -> None:
    db.session.execute(
        text(
            "SELECT setval("
            "pg_get_serial_sequence(:table_name, :column_name), "
            f"COALESCE((SELECT MAX({column_name}) FROM {table_name}), 1), "
            f"(SELECT MAX({column_name}) IS NOT NULL FROM {table_name})"
            ")"
        ),
        {"table_name": table_name, "column_name": column_name},
    )
