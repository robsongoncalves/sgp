from __future__ import annotations

import hashlib
import os

from app.extensions import db
from app.models import User
from app.repositories.utils import bool_value


class UsersRepository:
    def list(self) -> list[dict]:
        users = User.query.order_by(User.name.asc()).all()
        return [self._to_public_dict(user) for user in users]

    def get(self, user_id: int) -> User | None:
        return db.session.get(User, user_id)

    def get_public(self, user_id: int) -> dict | None:
        user = self.get(user_id)

        if user is None:
            return None

        return self._to_public_dict(user)

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data, require_password=True)
        if error:
            return None, error

        email = str(data["email"]).strip().lower()

        if self._email_exists(email):
            return None, "Ja existe um usuario cadastrado com este email."

        user = User(
            name=str(data["name"]).strip(),
            email=email,
            password_hash=self._hash_password(str(data["password"])),
            siape=str(data.get("siape", "")).strip(),
            cargo=str(data.get("cargo", "")).strip(),
            classe_nivel=str(data.get("classe_nivel", data.get("classeNivel", ""))).strip(),
            local_exercicio=str(data.get("local_exercicio", data.get("localExercicio", ""))).strip(),
            telefone=str(data.get("telefone", "")).strip(),
            active=bool_value(data.get("active", True)),
        )
        db.session.add(user)
        db.session.commit()

        return self._to_public_dict(user), None

    def update(self, user_id: int, data: dict) -> tuple[dict | None, str | None]:
        error = self._validate(data, require_password=False)
        if error:
            return None, error

        user = self.get(user_id)

        if user is None:
            return None, "Usuario nao encontrado."

        email = str(data["email"]).strip().lower()
        if self._email_exists(email, ignore_user_id=user_id):
            return None, "Ja existe um usuario cadastrado com este email."

        user.name = str(data["name"]).strip()
        user.email = email
        user.siape = str(data.get("siape", "")).strip()
        user.cargo = str(data.get("cargo", "")).strip()
        user.classe_nivel = str(data.get("classe_nivel", data.get("classeNivel", ""))).strip()
        user.local_exercicio = str(data.get("local_exercicio", data.get("localExercicio", ""))).strip()
        user.telefone = str(data.get("telefone", "")).strip()
        if str(data.get("password", "")).strip():
            user.password_hash = self._hash_password(str(data["password"]))
        user.active = bool_value(data.get("active", True))
        db.session.commit()

        return self._to_public_dict(user), None

    def delete(self, user_id: int) -> bool:
        user = self.get(user_id)

        if user is None:
            return False

        db.session.delete(user)
        db.session.commit()
        return True

    def authenticate(self, email: str, password: str) -> tuple[dict | None, str | None]:
        normalized_email = str(email).strip().lower()
        normalized_password = str(password)

        if not normalized_email or not normalized_password:
            return None, "Informe email e senha."

        user = User.query.filter(User.email == normalized_email).first()

        if user is None or not self._verify_password(normalized_password, user.password_hash):
            return None, "Email ou senha invalidos."

        if not user.active:
            return None, "Usuario inativo."

        return self._to_public_dict(user), None

    def list_groups(self, user_id: int) -> list[dict] | None:
        user = self.get(user_id)

        if user is None:
            return None

        groups = sorted(user.groups, key=lambda group: group.name.lower())
        return [
            {
                "id": group.id,
                "name": group.name,
                "description": group.description,
                "active": group.active,
            }
            for group in groups
        ]

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

    def _email_exists(self, email: str, ignore_user_id: int | None = None) -> bool:
        query = User.query.filter(User.email == email.strip().lower())

        if ignore_user_id is not None:
            query = query.filter(User.id != ignore_user_id)

        return db.session.query(query.exists()).scalar()

    def _to_public_dict(self, user: User) -> dict:
        return {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "siape": user.siape,
            "cargo": user.cargo,
            "classe_nivel": user.classe_nivel,
            "local_exercicio": user.local_exercicio,
            "telefone": user.telefone,
            "active": user.active,
        }

    def _hash_password(self, password: str) -> str:
        salt = os.urandom(16).hex()
        password_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            100_000,
        ).hex()

        return f"pbkdf2_sha256$100000${salt}${password_hash}"

    def _verify_password(self, password: str, stored_hash: str) -> bool:
        if not stored_hash:
            return True

        parts = stored_hash.split("$")
        if len(parts) != 4 or parts[0] != "pbkdf2_sha256":
            return False

        _, iterations, salt, password_hash = parts
        candidate_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        ).hex()

        return candidate_hash == password_hash


users_repository = UsersRepository()
