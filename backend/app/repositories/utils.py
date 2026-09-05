from __future__ import annotations

from datetime import date, datetime


def bool_value(value) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.strip().lower() in {"1", "true", "sim", "yes", "on"}

    return bool(value)


def datetime_to_api(value: datetime | None) -> str:
    if value is None:
        return ""

    return value.replace(microsecond=0).isoformat()


def date_to_api(value: datetime | date | None) -> str:
    if value is None:
        return ""

    return value.date().isoformat() if isinstance(value, datetime) else value.isoformat()


def optional_int(value) -> int | None:
    if value in (None, ""):
        return None

    return int(value)

