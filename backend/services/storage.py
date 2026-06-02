from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from backend.config import Settings, settings
from shared.schemas import SessionSnapshot, ValidationReport


class Store:
    async def save_session(self, session: SessionSnapshot) -> None:
        raise NotImplementedError

    async def get_session(self, session_id: str) -> SessionSnapshot | None:
        raise NotImplementedError

    async def save_report(self, report: ValidationReport) -> None:
        raise NotImplementedError

    async def get_report(self, session_id: str) -> ValidationReport | None:
        raise NotImplementedError


class MemoryStore(Store):
    def __init__(self) -> None:
        self.sessions: dict[str, SessionSnapshot] = {}
        self.reports: dict[str, ValidationReport] = {}

    async def save_session(self, session: SessionSnapshot) -> None:
        session.updated_at = datetime.now(timezone.utc)
        self.sessions[session.session_id] = session

    async def get_session(self, session_id: str) -> SessionSnapshot | None:
        return self.sessions.get(session_id)

    async def save_report(self, report: ValidationReport) -> None:
        self.reports[report.session_id] = report

    async def get_report(self, session_id: str) -> ValidationReport | None:
        return self.reports.get(session_id)


class MongoStore(Store):
    def __init__(self, config: Settings = settings) -> None:
        self.config = config
        self._client: Any | None = None

    def _db(self) -> Any:
        if self._client is None:
            from motor.motor_asyncio import AsyncIOMotorClient

            self._client = AsyncIOMotorClient(self.config.mongodb_uri, serverSelectionTimeoutMS=1500)
        return self._client[self.config.mongodb_db]

    async def save_session(self, session: SessionSnapshot) -> None:
        session.updated_at = datetime.now(timezone.utc)
        await self._db().sessions.replace_one(
            {"session_id": session.session_id},
            session.model_dump(mode="json"),
            upsert=True,
        )

    async def get_session(self, session_id: str) -> SessionSnapshot | None:
        doc = await self._db().sessions.find_one({"session_id": session_id}, {"_id": 0})
        return SessionSnapshot.model_validate(doc) if doc else None

    async def save_report(self, report: ValidationReport) -> None:
        await self._db().reports.replace_one(
            {"session_id": report.session_id},
            report.model_dump(mode="json"),
            upsert=True,
        )

    async def get_report(self, session_id: str) -> ValidationReport | None:
        doc = await self._db().reports.find_one({"session_id": session_id}, {"_id": 0})
        return ValidationReport.model_validate(doc) if doc else None


async def build_store(config: Settings = settings) -> Store:
    if config.demo_mode:
        return MemoryStore()
    try:
        store = MongoStore(config)
        await store._db().command("ping")
        return store
    except Exception:
        return MemoryStore()

