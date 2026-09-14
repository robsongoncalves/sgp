from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.extensions import db


service_category_association = db.Table(
    "service_category_association",
    db.metadata,
    db.Column("service_id", ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
    db.Column("category_id", ForeignKey("service_categories.id", ondelete="CASCADE"), primary_key=True),
)


service_group_association = db.Table(
    "service_group_association",
    db.metadata,
    db.Column("service_id", ForeignKey("services.id", ondelete="CASCADE"), primary_key=True),
    db.Column("group_id", ForeignKey("user_groups.id", ondelete="CASCADE"), primary_key=True),
)


service_situation_document_type_association = db.Table(
    "service_situation_document_type_association",
    db.metadata,
    db.Column("situation_id", ForeignKey("service_situations.id", ondelete="CASCADE"), primary_key=True),
    db.Column("document_type_id", ForeignKey("document_types.id", ondelete="CASCADE"), primary_key=True),
)


user_group_members = db.Table(
    "user_group_members",
    db.metadata,
    db.Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    db.Column("group_id", ForeignKey("user_groups.id", ondelete="CASCADE"), primary_key=True),
    db.Column("is_group_admin", Boolean, nullable=False, default=False),
)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )


class User(db.Model, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(180), nullable=False, unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    siape: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    cargo: Mapped[str] = mapped_column(String(140), nullable=False, default="")
    classe_nivel: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    local_exercicio: Mapped[str] = mapped_column(String(180), nullable=False, default="")
    telefone: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    groups: Mapped[list["UserGroup"]] = relationship(
        secondary=user_group_members,
        back_populates="users",
    )


class UserGroup(db.Model, TimestampMixin):
    __tablename__ = "user_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    manager_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    manager: Mapped[User | None] = relationship(foreign_keys=[manager_user_id])
    users: Mapped[list[User]] = relationship(
        secondary=user_group_members,
        back_populates="groups",
    )
    services: Mapped[list["Service"]] = relationship(
        secondary=service_group_association,
        back_populates="groups",
    )


class ServiceCategory(db.Model, TimestampMixin):
    __tablename__ = "service_categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(140), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    services: Mapped[list["Service"]] = relationship(
        secondary=service_category_association,
        back_populates="categories",
    )


class DocumentType(db.Model, TimestampMixin):
    __tablename__ = "document_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    code: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    origin: Mapped[str] = mapped_column(String(40), nullable=False, default="requester")
    purpose: Mapped[str] = mapped_column(String(40), nullable=False, default="attachment")
    module_slug: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    form_template_id: Mapped[int | None] = mapped_column(
        ForeignKey("form_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    opinion_template_id: Mapped[int | None] = mapped_column(
        ForeignKey("opinion_templates.id", ondelete="SET NULL"),
        nullable=True,
    )
    linked_service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id", ondelete="SET NULL"),
        nullable=True,
    )
    linked_service_required_status: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    allowed_formats: Mapped[str] = mapped_column(String(180), nullable=False, default="PDF")
    required_by_default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    allow_multiple_files: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    form_template: Mapped["FormTemplate | None"] = relationship()
    opinion_template: Mapped["OpinionTemplate | None"] = relationship()
    linked_service: Mapped["Service | None"] = relationship(foreign_keys=[linked_service_id])
    situations: Mapped[list["ServiceSituation"]] = relationship(
        secondary=service_situation_document_type_association,
        back_populates="document_types",
    )


class FormTemplate(db.Model, TimestampMixin):
    __tablename__ = "form_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    execution_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="dynamic")
    fields_schema: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class OpinionTemplate(db.Model, TimestampMixin):
    __tablename__ = "opinion_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(120), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    execution_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="dynamic")
    default_responsible_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    decision_options: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    fields_schema: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    requires_justification: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    requires_signature: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    allow_attachments: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    default_responsible_group: Mapped[UserGroup | None] = relationship()


class Service(db.Model, TimestampMixin):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(220), nullable=False)
    slug: Mapped[str] = mapped_column(String(220), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    documentation_url: Mapped[str] = mapped_column(Text, nullable=False, default="")
    implementation_mode: Mapped[str] = mapped_column(String(40), nullable=False, default="custom_module")
    module_key: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    featured: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    categories: Mapped[list[ServiceCategory]] = relationship(
        secondary=service_category_association,
        back_populates="services",
    )
    groups: Mapped[list[UserGroup]] = relationship(
        secondary=service_group_association,
        back_populates="services",
    )
    situations: Mapped[list["ServiceSituation"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="ServiceSituation.display_order",
    )
    hooks: Mapped[list["ServiceHook"]] = relationship(
        back_populates="service",
        cascade="all, delete-orphan",
        order_by="ServiceHook.execution_order",
    )


class ServiceSituation(db.Model, TimestampMixin):
    __tablename__ = "service_situations"
    __table_args__ = (
        UniqueConstraint("service_id", "name", name="uq_service_situation_name"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(140), nullable=False)
    previous_situation_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_situations.id", ondelete="SET NULL"),
        nullable=True,
    )
    responsible_group_id: Mapped[int | None] = mapped_column(
        ForeignKey("user_groups.id", ondelete="SET NULL"),
        nullable=True,
    )
    is_initial: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_final: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_opinion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    requires_attachment: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    display_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    service: Mapped[Service] = relationship(back_populates="situations")
    previous_situation: Mapped["ServiceSituation | None"] = relationship(remote_side=[id])
    responsible_group: Mapped[UserGroup | None] = relationship()
    document_types: Mapped[list[DocumentType]] = relationship(
        secondary=service_situation_document_type_association,
        back_populates="situations",
    )


class ServiceHook(db.Model, TimestampMixin):
    __tablename__ = "service_hooks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    function_id: Mapped[int | None] = mapped_column(
        ForeignKey("automation_functions.id", ondelete="SET NULL"),
        nullable=True,
    )
    event_name: Mapped[str] = mapped_column(String(80), nullable=False)
    handler_key: Mapped[str] = mapped_column(String(180), nullable=False)
    config: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    execution_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    service: Mapped[Service] = relationship(back_populates="hooks")
    function: Mapped["AutomationFunction | None"] = relationship()
    executions: Mapped[list["ServiceHookExecution"]] = relationship(
        back_populates="hook",
        cascade="all, delete-orphan",
    )


class AutomationFunction(db.Model, TimestampMixin):
    __tablename__ = "automation_functions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(140), nullable=False, unique=True, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    language: Mapped[str] = mapped_column(String(40), nullable=False, default="python")
    source_code: Mapped[str] = mapped_column(Text, nullable=False, default="")
    timeout_seconds: Mapped[int] = mapped_column(Integer, nullable=False, default=10)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


class ServiceHookExecution(db.Model, TimestampMixin):
    __tablename__ = "service_hook_executions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hook_id: Mapped[int] = mapped_column(ForeignKey("service_hooks.id", ondelete="CASCADE"), nullable=False)
    service_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_requests.id", ondelete="SET NULL"),
        nullable=True,
    )
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    event_name: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="success")
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    messages: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    warnings: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    error_message: Mapped[str] = mapped_column(Text, nullable=False, default="")

    hook: Mapped[ServiceHook] = relationship(back_populates="executions")
    service_request: Mapped["ServiceRequest | None"] = relationship()
    user: Mapped[User | None] = relationship()


class ServiceRequest(db.Model, TimestampMixin):
    __tablename__ = "service_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    number: Mapped[str] = mapped_column(String(30), nullable=False, unique=True, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id", ondelete="RESTRICT"), nullable=False)
    requester_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    current_situation_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_situations.id", ondelete="SET NULL"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(120), nullable=False, default="Solicitado")
    form_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    canceled_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    service: Mapped[Service] = relationship()
    requester: Mapped[User] = relationship()
    current_situation: Mapped[ServiceSituation | None] = relationship()
    movements: Mapped[list["ServiceRequestMovement"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
    )
    attachments: Mapped[list["ServiceRequestAttachment"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
    )
    documents: Mapped[list["ServiceRequestDocument"]] = relationship(
        back_populates="service_request",
        cascade="all, delete-orphan",
        foreign_keys="ServiceRequestDocument.service_request_id",
    )


class ServiceRequestMovement(db.Model, TimestampMixin):
    __tablename__ = "service_request_movements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_request_id: Mapped[int] = mapped_column(
        ForeignKey("service_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    from_situation_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_situations.id", ondelete="SET NULL"),
        nullable=True,
    )
    to_situation_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_situations.id", ondelete="SET NULL"),
        nullable=True,
    )
    moved_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    opinion: Mapped[str] = mapped_column(Text, nullable=False, default="")

    service_request: Mapped[ServiceRequest] = relationship(back_populates="movements")
    moved_by: Mapped[User] = relationship()
    from_situation: Mapped[ServiceSituation | None] = relationship(foreign_keys=[from_situation_id])
    to_situation: Mapped[ServiceSituation | None] = relationship(foreign_keys=[to_situation_id])


class ServiceRequestDocument(db.Model, TimestampMixin):
    __tablename__ = "service_request_documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_request_id: Mapped[int] = mapped_column(
        ForeignKey("service_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_situation_id: Mapped[int] = mapped_column(
        ForeignKey("service_situations.id", ondelete="RESTRICT"),
        nullable=False,
    )
    document_type_id: Mapped[int] = mapped_column(
        ForeignKey("document_types.id", ondelete="RESTRICT"),
        nullable=False,
    )
    linked_service_request_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_requests.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    updated_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    assigned_to_group_id: Mapped[int | None] = mapped_column(ForeignKey("user_groups.id", ondelete="SET NULL"), nullable=True)
    decided_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    decided_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    decision: Mapped[str] = mapped_column(String(40), nullable=False, default="")
    decision_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    status: Mapped[str] = mapped_column(String(40), nullable=False, default="draft")
    content_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    service_request: Mapped[ServiceRequest] = relationship(
        back_populates="documents",
        foreign_keys=[service_request_id],
    )
    service_situation: Mapped[ServiceSituation] = relationship()
    document_type: Mapped[DocumentType] = relationship()
    linked_service_request: Mapped[ServiceRequest | None] = relationship(foreign_keys=[linked_service_request_id])
    created_by: Mapped[User] = relationship(foreign_keys=[created_by_user_id])
    updated_by: Mapped[User | None] = relationship(foreign_keys=[updated_by_user_id])
    assigned_to_user: Mapped[User | None] = relationship(foreign_keys=[assigned_to_user_id])
    assigned_to_group: Mapped[UserGroup | None] = relationship()
    decided_by: Mapped[User | None] = relationship(foreign_keys=[decided_by_user_id])
    attachments: Mapped[list["ServiceRequestAttachment"]] = relationship(back_populates="document")


class ServiceRequestAttachment(db.Model, TimestampMixin):
    __tablename__ = "service_request_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_request_id: Mapped[int] = mapped_column(
        ForeignKey("service_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    service_request_document_id: Mapped[int | None] = mapped_column(
        ForeignKey("service_request_documents.id", ondelete="SET NULL"),
        nullable=True,
    )
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bucket: Mapped[str] = mapped_column(String(120), nullable=False)
    object_key: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    context_type: Mapped[str] = mapped_column(String(80), nullable=False, default="")
    requirement_code: Mapped[str] = mapped_column(String(20), nullable=False, default="")
    item_index: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    service_request: Mapped[ServiceRequest] = relationship(back_populates="attachments")
    document: Mapped[ServiceRequestDocument | None] = relationship(back_populates="attachments")
    uploaded_by: Mapped[User] = relationship()
