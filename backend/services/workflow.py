from __future__ import annotations

import asyncio
import json
from collections import defaultdict
from contextlib import suppress
from dataclasses import dataclass

from agents.competitor_analysis import CompetitorAnalysisAgent
from agents.front_desk import FrontDeskAgent
from agents.legal import LegalAgent
from agents.market_research import MarketResearchAgent
from agents.report_generator import ReportGeneratorAgent
from agents.scoring import ScoringAgent
from backend.services.storage import Store
from rag.vertex_search import build_market_retriever
from shared.schemas import (
    AgentEvent,
    AgentName,
    AgentStatus,
    ClarificationRequest,
    SessionSnapshot,
    SessionStatus,
    ValidationReport,
    ValidationStartRequest,
    new_session_id,
)


@dataclass
class WorkflowAgents:
    front_desk: FrontDeskAgent
    market: MarketResearchAgent
    competitors: CompetitorAnalysisAgent
    legal: LegalAgent
    scoring: ScoringAgent
    report: ReportGeneratorAgent


def build_agents() -> WorkflowAgents:
    return WorkflowAgents(
        front_desk=FrontDeskAgent(),
        market=MarketResearchAgent(build_market_retriever()),
        competitors=CompetitorAnalysisAgent(),
        legal=LegalAgent(),
        scoring=ScoringAgent(),
        report=ReportGeneratorAgent(),
    )


class ValidationWorkflow:
    """Workflow-owned orchestration for the validation pipeline."""

    def __init__(self, store: Store, agents: WorkflowAgents | None = None) -> None:
        self.store = store
        self.agents = agents or build_agents()
        self.queues: dict[str, asyncio.Queue[str]] = defaultdict(asyncio.Queue)
        self.tasks: dict[str, asyncio.Task[None]] = {}

    async def start(self, request: ValidationStartRequest) -> SessionSnapshot:
        session = SessionSnapshot(
            session_id=new_session_id(),
            status=SessionStatus.RUNNING,
            progress=0,
            description=request.description,
        )
        await self.store.save_session(session)
        self.tasks[session.session_id] = asyncio.create_task(self._run(session.session_id, request))
        return session

    async def clarify(self, session_id: str, request: ClarificationRequest) -> SessionSnapshot | None:
        previous = await self.store.get_session(session_id)
        if previous is None:
            return None
        merged = ValidationStartRequest(description=previous.description, clarifications=request.answers)
        previous.status = SessionStatus.RUNNING
        previous.progress = 0
        previous.clarification_questions = []
        await self.store.save_session(previous)
        self.tasks[session_id] = asyncio.create_task(self._run(session_id, merged))
        return previous

    async def status(self, session_id: str) -> SessionSnapshot | None:
        return await self.store.get_session(session_id)

    async def report(self, session_id: str) -> ValidationReport | None:
        return await self.store.get_report(session_id)

    async def stream(self, session_id: str):
        queue = self.queues[session_id]
        while True:
            message = await queue.get()
            yield f"data: {message}\n\n"
            with suppress(json.JSONDecodeError):
                payload = json.loads(message)
                if payload.get("type") == "session_complete":
                    break

    async def _run(self, session_id: str, request: ValidationStartRequest) -> None:
        try:
            await self._event(session_id, AgentName.FRONT_DESK, AgentStatus.RUNNING, "Validating idea quality", 5)
            idea = await self.agents.front_desk.run(request.description, request.clarifications)
            if idea.needs_clarification:
                session = await self.store.get_session(session_id)
                if session:
                    session.status = SessionStatus.NEEDS_CLARIFICATION
                    session.progress = 12
                    session.active_agent = AgentName.FRONT_DESK
                    session.clarification_questions = idea.clarification_questions
                    await self.store.save_session(session)
                await self._event(
                    session_id,
                    AgentName.FRONT_DESK,
                    AgentStatus.COMPLETED,
                    "Clarification required before full validation",
                    12,
                    {"questions": idea.clarification_questions},
                )
                await self._complete(session_id, SessionStatus.NEEDS_CLARIFICATION)
                return
            await self._event(session_id, AgentName.FRONT_DESK, AgentStatus.COMPLETED, "Idea context extracted", 12)

            await self._event(session_id, AgentName.MARKET_RESEARCH, AgentStatus.RUNNING, "Researching market size and demand signals", 20)
            market_task = asyncio.create_task(self.agents.market.run(idea))
            competitor_task = asyncio.create_task(self._run_framework_agent(session_id, AgentName.COMPETITOR_ANALYSIS, 34, self.agents.competitors.run(idea)))
            legal_task = asyncio.create_task(self._run_framework_agent(session_id, AgentName.LEGAL, 48, self.agents.legal.run(idea)))

            market = await market_task
            await self._event(session_id, AgentName.MARKET_RESEARCH, AgentStatus.COMPLETED, "Market research complete", 58)
            competitors = await competitor_task
            legal = await legal_task

            await self._event(session_id, AgentName.SCORING, AgentStatus.RUNNING, "Computing validation scores", 72)
            scores = await self.agents.scoring.run(idea, market, competitors, legal)
            await self._event(session_id, AgentName.SCORING, AgentStatus.COMPLETED, "Scoring complete", 82)

            await self._event(session_id, AgentName.REPORT, AgentStatus.RUNNING, "Assembling validation report", 90)
            report = await self.agents.report.run(session_id, idea, market, competitors, legal, scores)
            await self.store.save_report(report)
            await self._event(session_id, AgentName.REPORT, AgentStatus.COMPLETED, "Report generated", 100)

            session = await self.store.get_session(session_id)
            if session:
                session.status = SessionStatus.COMPLETED
                session.progress = 100
                session.active_agent = None
                await self.store.save_session(session)
            await self._complete(session_id, SessionStatus.COMPLETED)
        except Exception as exc:
            session = await self.store.get_session(session_id)
            if session:
                session.status = SessionStatus.FAILED
                session.error = str(exc)
                await self.store.save_session(session)
            await self._complete(session_id, SessionStatus.FAILED, error=str(exc))

    async def _run_framework_agent(self, session_id: str, agent: AgentName, progress: float, awaitable):
        labels = {
            AgentName.COMPETITOR_ANALYSIS: "Building preliminary competitor framework",
            AgentName.LEGAL: "Screening legal and compliance risks",
        }
        await self._event(session_id, agent, AgentStatus.RUNNING, labels[agent], progress)
        output = await awaitable
        await self._event(session_id, agent, AgentStatus.COMPLETED, "Framework analysis complete", progress + 12)
        return output

    async def _event(
        self,
        session_id: str,
        agent: AgentName,
        status: AgentStatus,
        message: str,
        progress: float,
        metadata: dict | None = None,
    ) -> None:
        snapshot = await self.store.get_session(session_id)
        if snapshot:
            snapshot.progress = max(snapshot.progress, progress)
            snapshot.active_agent = agent if status == AgentStatus.RUNNING else snapshot.active_agent
            await self.store.save_session(snapshot)
        event = AgentEvent(
            session_id=session_id,
            agent=agent,
            status=status,
            message=message,
            progress=progress,
            metadata=metadata or {},
        )
        await self.queues[session_id].put(event.model_dump_json())

    async def _complete(self, session_id: str, status: SessionStatus, error: str | None = None) -> None:
        await self.queues[session_id].put(
            json.dumps(
                {
                    "type": "session_complete",
                    "session_id": session_id,
                    "status": status.value,
                    "error": error,
                }
            )
        )

