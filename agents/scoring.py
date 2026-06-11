from __future__ import annotations

from agents.base import AgentDescriptor, DomainAgent
from shared.schemas import (
    AgentName,
    CompetitorAnalysisOutput,
    ExtractedIdea,
    LegalAnalysisOutput,
    MarketResearchOutput,
    ValidationScores,
)


class ScoringAgent(DomainAgent):
    descriptor = AgentDescriptor(
        name=AgentName.SCORING,
        instruction="Compute a transparent five-dimension validation score from agent outputs.",
    )

    async def run(
        self,
        idea: ExtractedIdea,
        market: MarketResearchOutput,
        competitors: CompetitorAnalysisOutput,
        legal: LegalAnalysisOutput,
    ) -> ValidationScores:
        market_score = min(92, 45 + market.confidence * 35 + len(market.opportunities) * 3)
        saturation_penalty = {"low": 12, "medium": 24, "high": 38}.get(competitors.market_saturation.lower(), 28)
        competition_score = min(100, max(10, 55 + saturation_penalty - len(competitors.differentiation_opportunities) * 5))
        risk_base = {"low": 24, "medium": 48, "high": 74}.get(legal.overall_risk_level.lower(), 52)
        risk_score = min(100, risk_base + len(legal.compliance_risks) * 3)
        validation_score = min(95, idea.quality_score * 100)
        investor_score = (market_score * 0.35) + ((100 - competition_score) * 0.2) + ((100 - risk_score) * 0.2) + (validation_score * 0.25)
        grade = self._grade(investor_score)

        return ValidationScores(
            validation_score=round(validation_score, 1),
            market_opportunity_score=round(market_score, 1),
            competition_score=round(competition_score, 1),
            risk_score=round(risk_score, 1),
            investor_attractiveness_score=round(investor_score, 1),
            overall_grade=grade,
        )

    def _grade(self, score: float) -> str:
        if score >= 85:
            return "A"
        if score >= 75:
            return "B+"
        if score >= 65:
            return "B"
        if score >= 55:
            return "C+"
        if score >= 45:
            return "C"
        return "D"

