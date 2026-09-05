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
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

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


class ServiceRequestAttachment(db.Model, TimestampMixin):
    __tablename__ = "service_request_attachments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    service_request_id: Mapped[int] = mapped_column(
        ForeignKey("service_requests.id", ondelete="CASCADE"),
        nullable=False,
    )
    uploaded_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)
    original_name: Mapped[str] = mapped_column(String(255), nullable=False)
    mime_type: Mapped[str] = mapped_column(String(120), nullable=False, default="")
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    bucket: Mapped[str] = mapped_column(String(120), nullable=False)
    object_key: Mapped[str] = mapped_column(String(500), nullable=False)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False, default="")

    service_request: Mapped[ServiceRequest] = relationship(back_populates="attachments")
    uploaded_by: Mapped[User] = relationship()

