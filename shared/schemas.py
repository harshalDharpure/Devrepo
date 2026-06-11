from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def new_session_id() -> str:
    return f"vp_{uuid4().hex}"


class AgentName(str, Enum):
    FRONT_DESK = "front_desk"
    MARKET_RESEARCH = "market_research"
    COMPETITOR_ANALYSIS = "competitor_analysis"
    LEGAL = "legal"
    SCORING = "scoring"
    REPORT = "report"


class AgentStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class SessionStatus(str, Enum):
    RUNNING = "running"
    NEEDS_CLARIFICATION = "needs_clarification"
    COMPLETED = "completed"
    FAILED = "failed"


class ValidationStartRequest(BaseModel):
    description: str = Field(..., min_length=10)
    clarifications: dict[str, str] = Field(default_factory=dict)


class ClarificationRequest(BaseModel):
    answers: dict[str, str] = Field(default_factory=dict)


class AgentEvent(BaseModel):
    session_id: str
    agent: AgentName
    status: AgentStatus
    message: str
    timestamp: datetime = Field(default_factory=utc_now)
    progress: float = Field(ge=0, le=100)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvidenceCitation(BaseModel):
    source: str
    title: str
    snippet: str
    url: str | None = None
    relevance_score: float = Field(default=0.5, ge=0, le=1)


class ExtractedIdea(BaseModel):
    original_description: str
    idea_summary: str
    industry: str
    target_audience: str
    business_model: str
    geographies: list[str] = Field(default_factory=list)
    pricing: str | None = None
    keywords: list[str] = Field(default_factory=list)
    quality_score: float = Field(default=0.7, ge=0, le=1)
    needs_clarification: bool = False
    clarification_questions: list[str] = Field(default_factory=list)


class MarketResearchOutput(BaseModel):
    tam_usd: str
    sam_usd: str
    som_usd: str
    growth_rate: str
    trends: list[str] = Field(default_factory=list)
    opportunities: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    customer_segments: list[str] = Field(default_factory=list)
    buyer_personas: list[str] = Field(default_factory=list)
    go_to_market_signals: list[str] = Field(default_factory=list)
    evidence: list[EvidenceCitation] = Field(default_factory=list)
    confidence: float = Field(default=0.55, ge=0, le=1)


class CompetitorRecord(BaseModel):
    name: str
    description: str
    pricing: str
    business_model: str
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)


class CompetitorAnalysisOutput(BaseModel):
    direct_competitors: list[CompetitorRecord] = Field(default_factory=list)
    market_saturation: str = "unknown"
    differentiation_opportunities: list[str] = Field(default_factory=list)
    swot: dict[str, list[str]] = Field(default_factory=dict)
    evidence: list[EvidenceCitation] = Field(default_factory=list)
    confidence: float = Field(default=0.35, ge=0, le=1)


class LegalAnalysisOutput(BaseModel):
    compliance_risks: list[str] = Field(default_factory=list)
    regulations: list[str] = Field(default_factory=list)
    licensing_requirements: list[str] = Field(default_factory=list)
    privacy_concerns: list[str] = Field(default_factory=list)
    geography_specific: dict[str, list[str]] = Field(default_factory=dict)
    overall_risk_level: str = "medium"
    evidence: list[EvidenceCitation] = Field(default_factory=list)
    confidence: float = Field(default=0.3, ge=0, le=1)


class ValidationScores(BaseModel):
    validation_score: float = Field(ge=0, le=100)
    market_opportunity_score: float = Field(ge=0, le=100)
    competition_score: float = Field(ge=0, le=100)
    risk_score: float = Field(ge=0, le=100)
    investor_attractiveness_score: float = Field(ge=0, le=100)
    overall_grade: str


class LeanCanvas(BaseModel):
    problem: str
    solution: str
    unique_value_proposition: str
    unfair_advantage: str
    customer_segments: str
    key_metrics: str
    channels: str
    cost_structure: str
    revenue_streams: str


class ValidationReport(BaseModel):
    session_id: str
    idea_summary: str
    executive_summary: str
    key_risks: list[str]
    recommendations: list[str]
    lean_canvas: LeanCanvas
    swot: dict[str, list[str]]
    scores: ValidationScores
    market_research: MarketResearchOutput
    competitor_analysis: CompetitorAnalysisOutput
    legal_analysis: LegalAnalysisOutput
    evidence_citations: list[EvidenceCitation]
    generated_at: datetime = Field(default_factory=utc_now)


class SessionSnapshot(BaseModel):
    session_id: str
    status: SessionStatus
    progress: float = Field(ge=0, le=100)
    description: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    active_agent: AgentName | None = None
    clarification_questions: list[str] = Field(default_factory=list)
    error: str | None = None

