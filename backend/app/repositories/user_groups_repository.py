from __future__ import annotations

from sqlalchemy import delete, insert, select

from app.extensions import db
from app.models import User, UserGroup, user_group_members
from app.repositories.utils import bool_value, optional_int


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
            return None, "Ja existe uma unidade cadastrada com este nome."

        group = UserGroup(
            name=name,
            description=str(data.get("description", "")).strip(),
            parent_group_id=self._parent_group_id(data),
            manager_user_id=self._manager_user_id(data),
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
            return None, "Unidade nao encontrada."

        name = str(data["name"]).strip()
        if self._name_exists(name, ignore_group_id=group_id):
            return None, "Ja existe uma unidade cadastrada com este nome."

        parent_group_id = self._parent_group_id(data)
        hierarchy_error = self._validate_hierarchy(group, parent_group_id)
        if hierarchy_error:
            return None, hierarchy_error

        group.name = name
        group.description = str(data.get("description", "")).strip()
        group.parent_group_id = parent_group_id
        group.manager_user_id = self._manager_user_id(data)
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
            return "Informe o nome da unidade."

        parent_group_id = self._parent_group_id(data)
        if parent_group_id is not None and db.session.get(UserGroup, parent_group_id) is None:
            return "Unidade pai nao encontrada."

        manager_user_id = self._manager_user_id(data)
        if manager_user_id is not None and db.session.get(User, manager_user_id) is None:
            return "Usuario informado como chefia nao encontrado."

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
            "parent_group_id": group.parent_group_id,
            "parent_group_name": group.parent.name if group.parent else "",
            "manager_user_id": group.manager_user_id,
            "manager_name": group.manager.name if group.manager else "",
            "manager_email": group.manager.email if group.manager else "",
            "active": group.active,
        }

    def _manager_user_id(self, data: dict) -> int | None:
        return optional_int(data.get("manager_user_id"))

    def _parent_group_id(self, data: dict) -> int | None:
        return optional_int(data.get("parent_group_id"))

    def _validate_hierarchy(self, group: UserGroup, parent_group_id: int | None) -> str | None:
        if parent_group_id is None:
            return None

        if parent_group_id == group.id:
            return "Uma unidade nao pode ser filha dela mesma."

        current = db.session.get(UserGroup, parent_group_id)
        visited_group_ids: set[int] = set()

        while current is not None:
            if current.id == group.id:
                return "Hierarquia invalida: a unidade pai escolhida criaria um ciclo."

            if current.id in visited_group_ids:
                return "Hierarquia invalida: foi detectado um ciclo entre unidades."

            visited_group_ids.add(current.id)
            current = current.parent


user_groups_repository = UserGroupsRepository()
