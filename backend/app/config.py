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
    JSON_SORT_KEYS = False
