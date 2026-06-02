from __future__ import annotations

import os
from dataclasses import dataclass


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    demo_mode: bool = _bool_env("DEMO_MODE", True)
    use_mock_retrieval: bool = _bool_env("USE_MOCK_RETRIEVAL", True)
    debug: bool = _bool_env("DEBUG", False)

    google_api_key: str | None = os.getenv("GOOGLE_API_KEY")
    gemini_model: str = os.getenv("GEMINI_MODEL", "gemini-2.5-pro")
    google_genai_use_vertexai: bool = _bool_env("GOOGLE_GENAI_USE_VERTEXAI", False)
    google_cloud_project: str | None = os.getenv("GOOGLE_CLOUD_PROJECT")
    google_cloud_location: str = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

    vertex_search_data_store: str | None = os.getenv("VERTEX_SEARCH_DATA_STORE")
    vertex_search_location: str = os.getenv("VERTEX_SEARCH_LOCATION", "global")

    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    mongodb_db: str = os.getenv("MONGODB_DB", "venturepilot")

    cors_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")
        if origin.strip()
    )


settings = Settings()

