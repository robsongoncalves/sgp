from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from threading import Lock

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "user_groups.json"
MEMBERS_FILE = BASE_DIR / "data" / "user_group_members.json"


@dataclass
class UserGroup:
    id: int
    name: str
    description: str = ""
    active: bool = True


class UserGroupsRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._ensure_data_file()

    def list(self) -> list[dict]:
        return [asdict(group) for group in self._read_groups()]

    def get(self, group_id: int) -> UserGroup | None:
        return next((group for group in self._read_groups() if group.id == group_id), None)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data)
        if error:
            return None, error

        with self._lock:
            groups = self._read_groups()

            if self._name_exists(data["name"], groups=groups):
                return None, "Ja existe um grupo cadastrado com este nome."

            group = UserGroup(
                id=self._next_id(groups),
                name=data["name"].strip(),
                description=str(data.get("description", "")).strip(),
                active=bool(data.get("active", True)),
            )
            groups.append(group)
            self._write_groups(groups)

        return asdict(group), None

    def update(self, group_id: int, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data)
        if error:
            return None, error

        with self._lock:
            groups = self._read_groups()
            group = next((item for item in groups if item.id == group_id), None)

            if group is None:
                return None, "Grupo nao encontrado."

            if self._name_exists(data["name"], ignore_group_id=group_id, groups=groups):
                return None, "Ja existe um grupo cadastrado com este nome."

            group.name = data["name"].strip()
            group.description = str(data.get("description", "")).strip()
            group.active = bool(data.get("active", True))
            self._write_groups(groups)

        return asdict(group), None

    def delete(self, group_id: int) -> bool:
        with self._lock:
            groups = self._read_groups()
            group = next((item for item in groups if item.id == group_id), None)

            if group is None:
                return False

            groups.remove(group)
            self._write_groups(groups)
            memberships = [
                item for item in self._read_memberships()
                if item["group_id"] != group_id
            ]
            self._write_memberships(memberships)
            return True

    def get_member_user_ids(self, group_id: int) -> list[int] | None:
        if self.get(group_id) is None:
            return None

        memberships = self._read_memberships()
        membership = next(
            (item for item in memberships if item["group_id"] == group_id),
            None,
        )

        if membership is None:
            return []

        return membership["user_ids"]

    def set_member_user_ids(self, group_id: int, user_ids: list[int]) -> list[int] | None:
        if self.get(group_id) is None:
            return None

        normalized_user_ids = sorted(set(int(user_id) for user_id in user_ids))

        with self._lock:
            memberships = self._read_memberships()
            membership = next(
                (item for item in memberships if item["group_id"] == group_id),
                None,
            )

            if membership is None:
                memberships.append({
                    "group_id": group_id,
                    "user_ids": normalized_user_ids,
                })
            else:
                membership["user_ids"] = normalized_user_ids

            self._write_memberships(memberships)

        return normalized_user_ids

    def _validate(self, data: dict) -> str | None:
        name = str(data.get("name", "")).strip()

        if not name:
            return "Informe o nome do grupo."

        return None

    def _name_exists(
        self,
        name: str,
        groups: list[UserGroup],
        ignore_group_id: int | None = None,
    ) -> bool:
        normalized_name = name.strip().lower()
        return any(
            group.name.lower() == normalized_name and group.id != ignore_group_id
            for group in groups
        )

    def _read_groups(self) -> list[UserGroup]:
        with DATA_FILE.open(encoding="utf-8") as file:
            data = json.load(file)

        return [
            UserGroup(
                id=item["id"],
                name=item["name"],
                description=item.get("description", ""),
                active=item.get("active", True),
            )
            for item in data
        ]

    def _write_groups(self, groups: list[UserGroup]) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump([asdict(group) for group in groups], file, ensure_ascii=True, indent=2)
            file.write("\n")

    def _ensure_data_file(self) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not DATA_FILE.exists():
            self._write_groups([])

        if not MEMBERS_FILE.exists():
            self._write_memberships([])

    def _next_id(self, groups: list[UserGroup]) -> int:
        if not groups:
            return 1

        return max(group.id for group in groups) + 1

    def _read_memberships(self) -> list[dict]:
        with MEMBERS_FILE.open(encoding="utf-8") as file:
            data = json.load(file)

        return [
            {
                "group_id": int(item["group_id"]),
                "user_ids": [int(user_id) for user_id in item.get("user_ids", [])],
            }
            for item in data
        ]

    def _write_memberships(self, memberships: list[dict]) -> None:
        MEMBERS_FILE.parent.mkdir(parents=True, exist_ok=True)

        with MEMBERS_FILE.open("w", encoding="utf-8") as file:
            json.dump(memberships, file, ensure_ascii=True, indent=2)
            file.write("\n")


user_groups_repository = UserGroupsRepository()
