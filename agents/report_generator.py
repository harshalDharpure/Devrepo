from __future__ import annotations

import json

from agents.base import AdkExecutionError, AgentDescriptor, DomainAgent
from shared.schemas import (
    AgentName,
    CompetitorAnalysisOutput,
    ExtractedIdea,
    LeanCanvas,
    LegalAnalysisOutput,
    MarketResearchOutput,
    ValidationReport,
    ValidationScores,
    EvidenceCitation,
)


class ReportGeneratorAgent(DomainAgent):
    descriptor = AgentDescriptor(
        name=AgentName.REPORT,
        instruction="Generate the final startup validation report from workflow state.",
        output_schema=ValidationReport,
    )

    async def run(
        self,
        session_id: str,
        idea: ExtractedIdea,
        market: MarketResearchOutput,
        competitors: CompetitorAnalysisOutput,
        legal: LegalAnalysisOutput,
        scores: ValidationScores,
    ) -> ValidationReport:
        report = self._deterministic_report(session_id, idea, market, competitors, legal, scores)
        if self.adk_enabled:
            try:
                return await self._run_with_adk(report)
            except (AdkExecutionError, ValueError, json.JSONDecodeError):
                pass
        return report

    async def _run_with_adk(self, draft: ValidationReport) -> ValidationReport:
        prompt = f"""
Polish this startup validation report while preserving its schema, scores, evidence citations, and core findings.

Return JSON only matching the same object shape. You may improve:
- executive_summary
- recommendations
- key_risks wording
- lean_canvas wording
- swot wording

Do not remove required fields. Do not invent citations or URLs.

Draft report:
{draft.model_dump_json(indent=2)}
"""
        payload = await self.run_adk_json(prompt)
        payload.setdefault("session_id", draft.session_id)
        payload.setdefault("scores", draft.scores.model_dump())
        payload.setdefault("market_research", draft.market_research.model_dump())
        payload.setdefault("competitor_analysis", draft.competitor_analysis.model_dump())
        payload.setdefault("legal_analysis", draft.legal_analysis.model_dump())
        payload.setdefault("evidence_citations", [item.model_dump() for item in draft.evidence_citations])
        return ValidationReport.model_validate(payload)

    def _deterministic_report(
        self,
        session_id: str,
        idea: ExtractedIdea,
        market: MarketResearchOutput,
        competitors: CompetitorAnalysisOutput,
        legal: LegalAnalysisOutput,
        scores: ValidationScores,
    ) -> ValidationReport:
        key_risks = list(dict.fromkeys(market.risks + legal.compliance_risks + competitors.swot.get("threats", [])))[:6]
        recommendations = [
            "Run 5-10 design-partner interviews in the highest-urgency customer segment.",
            "Validate willingness to pay with a paid pilot before broad product build-out.",
            "Instrument evidence quality, time saved, and decision confidence as core product metrics.",
            "Upgrade competitor and legal research with live specialist sources before fundraising claims.",
        ]
        evidence = list(dict.fromkeys([item.model_dump_json() for item in market.evidence + competitors.evidence + legal.evidence]))

        return ValidationReport(
            session_id=session_id,
            idea_summary=idea.idea_summary,
            executive_summary=self._executive_summary(idea, market, competitors, legal, scores),
            key_risks=key_risks,
            recommendations=recommendations,
            lean_canvas=self._lean_canvas(idea, market),
            swot=self._swot(market, competitors, legal),
            scores=scores,
            market_research=market,
            competitor_analysis=competitors,
            legal_analysis=legal,
            evidence_citations=[EvidenceCitation.model_validate_json(item) for item in evidence],
        )

    def _executive_summary(
        self,
        idea: ExtractedIdea,
        market: MarketResearchOutput,
        competitors: CompetitorAnalysisOutput,
        legal: LegalAnalysisOutput,
        scores: ValidationScores,
    ) -> str:
        return (
            f"{idea.idea_summary}\n\n"
            f"The market signal is directionally promising: estimated TAM is {market.tam_usd}, "
            f"with a reachable SAM of {market.sam_usd} and an initial SOM of {market.som_usd}. "
            f"Growth outlook is {market.growth_rate}. Competition is currently assessed as "
            f"{competitors.market_saturation}, while legal risk is {legal.overall_risk_level}. "
            f"The resulting investor attractiveness score is {scores.investor_attractiveness_score:.0f}/100 "
            f"with an overall grade of {scores.overall_grade}."
        )

    def _lean_canvas(self, idea: ExtractedIdea, market: MarketResearchOutput) -> LeanCanvas:
        return LeanCanvas(
            problem=f"{idea.target_audience} need faster, more reliable evidence for startup validation decisions.",
            solution=idea.idea_summary,
            unique_value_proposition="Evidence-grounded validation reports generated through specialist AI agents.",
            unfair_advantage="Workflow depth, retrieval-backed citations, and repeatable scoring methodology.",
            customer_segments=", ".join(market.customer_segments[:3]) or idea.target_audience,
            key_metrics="Paid pilots, report completion rate, retained weekly usage, time saved, confidence lift",
            channels="Founder communities, investor networks, accelerators, content-led SEO, partner advisors",
            cost_structure="LLM inference, retrieval infrastructure, data licensing, cloud hosting, support",
            revenue_streams=idea.pricing or idea.business_model,
        )

    def _swot(
        self,
        market: MarketResearchOutput,
        competitors: CompetitorAnalysisOutput,
        legal: LegalAnalysisOutput,
    ) -> dict[str, list[str]]:
        return {
            "strengths": competitors.swot.get("strengths", []) + market.opportunities[:1],
            "weaknesses": competitors.swot.get("weaknesses", []) + ["Specialist analysis depth is still incomplete"],
            "opportunities": market.opportunities[:3],
            "threats": competitors.swot.get("threats", []) + legal.compliance_risks[:2],
        }
