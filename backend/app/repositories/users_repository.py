from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import os
from pathlib import Path
from threading import Lock

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "users.json"


@dataclass
class User:
    id: int
    name: str
    email: str
    password_hash: str = ""
    active: bool = True


class UsersRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._ensure_data_file()

    def list(self) -> list[dict]:
        return [self._to_public_dict(user) for user in self._read_users()]

    def get(self, user_id: int) -> User | None:
        return next((user for user in self._read_users() if user.id == user_id), None)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data, require_password=True)
        if error:
            return None, error

        with self._lock:
            users = self._read_users()

            if self._email_exists(data["email"], users=users):
                return None, "Ja existe um usuario cadastrado com este email."

            user = User(
                id=self._next_id(users),
                name=data["name"].strip(),
                email=data["email"].strip().lower(),
                password_hash=self._hash_password(data["password"]),
                active=bool(data.get("active", True)),
            )
            users.append(user)
            self._write_users(users)

        return self._to_public_dict(user), None

    def update(self, user_id: int, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data, require_password=False)
        if error:
            return None, error

        email = data["email"].strip().lower()

        with self._lock:
            users = self._read_users()
            user = next((item for item in users if item.id == user_id), None)

            if user is None:
                return None, "Usuario nao encontrado."

            if self._email_exists(email, ignore_user_id=user_id, users=users):
                return None, "Ja existe um usuario cadastrado com este email."

            user.name = data["name"].strip()
            user.email = email
            if "password" in data and str(data["password"]).strip():
                user.password_hash = self._hash_password(data["password"])
            user.active = bool(data.get("active", True))
            self._write_users(users)

        return self._to_public_dict(user), None

    def delete(self, user_id: int) -> bool:
        with self._lock:
            users = self._read_users()
            user = next((item for item in users if item.id == user_id), None)

            if user is None:
                return False

            users.remove(user)
            self._write_users(users)
            return True

    def _validate(self, data: dict, require_password: bool) -> str | None:
        name = str(data.get("name", "")).strip()
        email = str(data.get("email", "")).strip().lower()
        password = str(data.get("password", "")).strip()

        if not name:
            return "Informe o nome do usuario."

        if not email:
            return "Informe o email do usuario."

        if "@" not in email:
            return "Informe um email valido."

        if require_password and not password:
            return "Informe a senha do usuario."

        return None

    def _email_exists(
        self,
        email: str,
        users: list[User],
        ignore_user_id: int | None = None,
    ) -> bool:
        normalized_email = email.strip().lower()
        return any(
            user.email == normalized_email and user.id != ignore_user_id
            for user in users
        )

    def _to_public_dict(self, user: User) -> dict:
        data = asdict(user)
        data.pop("password_hash")
        return data

    def _read_users(self) -> list[User]:
        with DATA_FILE.open(encoding="utf-8") as file:
            data = json.load(file)

        return [
            User(
                id=item["id"],
                name=item["name"],
                email=item["email"],
                password_hash=item.get("password_hash", ""),
                active=item.get("active", True),
            )
            for item in data
        ]

    def _write_users(self, users: list[User]) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump([asdict(user) for user in users], file, ensure_ascii=True, indent=2)
            file.write("\n")

    def _ensure_data_file(self) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not DATA_FILE.exists():
            self._write_users([])

    def _next_id(self, users: list[User]) -> int:
        if not users:
            return 1

        return max(user.id for user in users) + 1

    def _hash_password(self, password: str) -> str:
        salt = os.urandom(16).hex()
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            str(password).encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        ).hex()

        return f"pbkdf2_sha256$100000${salt}${password_hash}"


users_repository = UsersRepository()
