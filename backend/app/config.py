from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://sgp:sgp@localhost:5432/sgp",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }
    ATTACHMENT_STORAGE_DRIVER = os.getenv("ATTACHMENT_STORAGE_DRIVER", "local").lower()
    ATTACHMENT_LOCAL_PATH = os.getenv(
        "ATTACHMENT_LOCAL_PATH",
        str(BASE_DIR / "storage" / "uploads"),
    )
    DOCUMENTATION_ALLOWED_HOSTS = [
        host.strip().lower()
        for host in os.getenv("DOCUMENTATION_ALLOWED_HOSTS", ".unipampa.edu.br,unipampa.edu.br").split(",")
        if host.strip()
    ]
    DOCUMENTATION_PLAYWRIGHT_ENABLED = os.getenv("DOCUMENTATION_PLAYWRIGHT_ENABLED", "true").lower() == "true"
    DOCUMENTATION_PLAYWRIGHT_TIMEOUT_MS = int(os.getenv("DOCUMENTATION_PLAYWRIGHT_TIMEOUT_MS", "20000"))
    DOCUMENTATION_PLAYWRIGHT_PROXY = os.getenv("DOCUMENTATION_PLAYWRIGHT_PROXY", "").strip()
    JSON_SORT_KEYS = False
