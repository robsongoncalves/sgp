from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
from threading import Lock

from app.repositories.services_repository import Service, services_repository

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_FILE = BASE_DIR / "data" / "service_requests.json"
DEV_REQUESTER_USER_ID = 3


@dataclass
class ServiceRequest:
    id: int
    number: str
    service_id: int
    service_name: str
    service_slug: str
    module_key: str
    requester_user_id: int
    current_situation_id: int | None
    current_situation_name: str
    status: str
    created_at: str
    updated_at: str
    canceled_at: str | None = None


class ServiceRequestsRepository:
    def __init__(self) -> None:
        self._lock = Lock()
        self._ensure_data_file()

    def list(self, requester_user_id: int | None = None) -> list[dict]:
        requests = self._read_requests()

        if requester_user_id is not None:
            requests = [
                request
                for request in requests
                if request.requester_user_id == requester_user_id
            ]

        requests = sorted(
            requests,
            key=lambda request: request.created_at,
            reverse=True,
        )
        return [asdict(request) for request in requests]

    def create(self, data: dict) -> tuple[dict | None, str | None]:
        service = self._find_service(data)

        if service is None:
            return None, "Servico nao encontrado."

        if not service.active:
            return None, "Servico inativo."

        now = datetime.now().replace(microsecond=0).isoformat()
        initial_situation = next(
            (situation for situation in service.situations if situation.is_initial),
            service.situations[0] if service.situations else None,
        )
        requester_user_id = self._optional_int(data.get("requester_user_id")) or DEV_REQUESTER_USER_ID

        with self._lock:
            requests = self._read_requests()
            next_id = self._next_id(requests)
            request = ServiceRequest(
                id=next_id,
                number=self._request_number(next_id),
                service_id=service.id,
                service_name=service.name,
                service_slug=service.slug,
                module_key=service.module_key,
                requester_user_id=requester_user_id,
                current_situation_id=initial_situation.id if initial_situation else None,
                current_situation_name=initial_situation.name if initial_situation else "Solicitado",
                status=initial_situation.name if initial_situation else "Solicitado",
                created_at=now,
                updated_at=now,
            )
            requests.append(request)
            self._write_requests(requests)

        return asdict(request), None

    def _find_service(self, data: dict) -> Service | None:
        service_id = self._optional_int(data.get("service_id"))
        service_slug = str(data.get("service_slug", "")).strip()
        services = services_repository._read_services()

        if service_id is not None:
            return next((service for service in services if service.id == service_id), None)

        if service_slug:
            return next((service for service in services if service.slug == service_slug), None)

        return None

    def _read_requests(self) -> list[ServiceRequest]:
        with DATA_FILE.open(encoding="utf-8") as file:
            data = json.load(file)

        return [
            ServiceRequest(
                id=item["id"],
                number=item["number"],
                service_id=item["service_id"],
                service_name=item["service_name"],
                service_slug=item["service_slug"],
                module_key=item.get("module_key", ""),
                requester_user_id=item.get("requester_user_id", DEV_REQUESTER_USER_ID),
                current_situation_id=self._optional_int(item.get("current_situation_id")),
                current_situation_name=item.get("current_situation_name", item.get("status", "Solicitado")),
                status=item.get("status", item.get("current_situation_name", "Solicitado")),
                created_at=item["created_at"],
                updated_at=item.get("updated_at", item["created_at"]),
                canceled_at=item.get("canceled_at"),
            )
            for item in data
        ]

    def _write_requests(self, requests: list[ServiceRequest]) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        with DATA_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                [asdict(request) for request in requests],
                file,
                ensure_ascii=True,
                indent=2,
            )
            file.write("\n")

    def _ensure_data_file(self) -> None:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)

        if not DATA_FILE.exists():
            self._write_requests([])

    def _next_id(self, requests: list[ServiceRequest]) -> int:
        if not requests:
            return 1

        return max(request.id for request in requests) + 1

    def _request_number(self, request_id: int) -> str:
        return f"{datetime.now():%Y%m%d}{request_id:05d}"

    def _optional_int(self, value) -> int | None:
        if value in (None, ""):
            return None

        return int(value)


service_requests_repository = ServiceRequestsRepository()
