from __future__ import annotations

from sqlalchemy import delete, insert, select

from app.extensions import db
from app.models import User, UserGroup, user_group_members
from app.repositories.utils import bool_value


class UserGroupsRepository:
    def list(self) -> list[dict]:
        groups = UserGroup.query.order_by(UserGroup.name.asc()).all()
        return [self._to_dict(group) for group in groups]

    def list_by_user(self, user_id: int) -> list[dict] | None:
        user = db.session.get(User, user_id)

        if user is None:
            return None

        if user.email == "admin@unipampa.edu.br":
            return [
                self._to_dict(group)
                for group in UserGroup.query.filter(UserGroup.active.is_(True))
                .order_by(UserGroup.name.asc())
                .all()
            ]

        groups = sorted(user.groups, key=lambda group: group.name.lower())
        return [self._to_dict(group) for group in groups if group.active]

    def get(self, group_id: int) -> UserGroup | None:
        return db.session.get(UserGroup, group_id)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data)
        if error:
            return None, error

        name = str(data["name"]).strip()
        if self._name_exists(name):
            return None, "Ja existe um grupo cadastrado com este nome."

        group = UserGroup(
            name=name,
            description=str(data.get("description", "")).strip(),
            active=bool_value(data.get("active", True)),
        )
        db.session.add(group)
        db.session.commit()

        return self._to_dict(group), None

    def update(self, group_id: int, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data)
        if error:
            return None, error

        group = self.get(group_id)

        if group is None:
            return None, "Grupo nao encontrado."

        name = str(data["name"]).strip()
        if self._name_exists(name, ignore_group_id=group_id):
            return None, "Ja existe um grupo cadastrado com este nome."

        group.name = name
        group.description = str(data.get("description", "")).strip()
        group.active = bool_value(data.get("active", True))
        db.session.commit()

        return self._to_dict(group), None

    def delete(self, group_id: int) -> bool:
        group = self.get(group_id)

        if group is None:
            return False

        db.session.delete(group)
        db.session.commit()
        return True

    def get_member_user_ids(self, group_id: int) -> list[int] | None:
        if self.get(group_id) is None:
            return None

        rows = db.session.execute(
            select(user_group_members.c.user_id)
            .where(user_group_members.c.group_id == group_id)
            .order_by(user_group_members.c.user_id.asc())
        ).all()

        return [row.user_id for row in rows]

    def set_member_user_ids(self, group_id: int, user_ids: list[int]) -> list[int] | None:
        if self.get(group_id) is None:
            return None

        existing_user_ids = {
            user.id
            for user in User.query.filter(User.id.in_([int(user_id) for user_id in user_ids])).all()
        }
        normalized_user_ids = sorted(existing_user_ids)

        db.session.execute(
            delete(user_group_members).where(user_group_members.c.group_id == group_id)
        )

        if normalized_user_ids:
            db.session.execute(
                insert(user_group_members),
                [
                    {
                        "group_id": group_id,
                        "user_id": user_id,
                        "is_group_admin": False,
                    }
                    for user_id in normalized_user_ids
                ],
            )

        db.session.commit()
        return normalized_user_ids

    def _validate(self, data: dict) -> str | None:
        name = str(data.get("name", "")).strip()

        if not name:
            return "Informe o nome do grupo."

        return None

    def _name_exists(self, name: str, ignore_group_id: int | None = None) -> bool:
        query = UserGroup.query.filter(UserGroup.name.ilike(name.strip()))

        if ignore_group_id is not None:
            query = query.filter(UserGroup.id != ignore_group_id)

        return db.session.query(query.exists()).scalar()

    def _to_dict(self, group: UserGroup) -> dict:
        return {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "active": group.active,
        }


user_groups_repository = UserGroupsRepository()
