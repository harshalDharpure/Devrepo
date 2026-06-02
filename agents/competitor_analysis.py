from __future__ import annotations

from agents.base import AgentDescriptor, DomainAgent
from shared.schemas import AgentName, CompetitorAnalysisOutput, CompetitorRecord, EvidenceCitation, ExtractedIdea


class CompetitorAnalysisAgent(DomainAgent):
    descriptor = AgentDescriptor(
        name=AgentName.COMPETITOR_ANALYSIS,
        instruction=(
            "Map direct and adjacent competitors, saturation, SWOT, and differentiation. "
            "This implementation is intentionally a basic framework pending specialist enrichment."
        ),
    )

    async def run(self, idea: ExtractedIdea) -> CompetitorAnalysisOutput:
        category = idea.industry.title()
        return CompetitorAnalysisOutput(
            direct_competitors=[
                CompetitorRecord(
                    name=f"Horizontal {category} workflow platforms",
                    description="Broad platforms that can approximate parts of the workflow with configuration.",
                    pricing="Varies by seat or usage",
                    business_model="SaaS",
                    strengths=["Existing distribution", "Broad feature coverage"],
                    weaknesses=["Less specialized evidence model", "May require manual setup"],
                ),
                CompetitorRecord(
                    name="Consultants and analyst services",
                    description="Human-led research services that produce bespoke market or compliance reports.",
                    pricing="Project-based",
                    business_model="Services",
                    strengths=["High-trust expert judgment", "Custom deliverables"],
                    weaknesses=["Slower turnaround", "Higher marginal cost"],
                ),
            ],
            market_saturation="medium",
            differentiation_opportunities=[
                "Expose evidence citations and confidence instead of opaque recommendations",
                "Specialize the workflow for a high-frequency customer segment before expanding horizontally",
                "Automate repeatable research while preserving expert review hooks",
            ],
            swot={
                "strengths": ["Clear automation wedge", "Potential for repeatable report workflows"],
                "weaknesses": ["Competitive map needs live web intelligence", "Positioning may be broad initially"],
                "opportunities": ["Vertical specialization", "Integrations and evidence provenance"],
                "threats": ["Feature copying by incumbents", "Services firms bundling lightweight automation"],
            },
            evidence=[
                EvidenceCitation(
                    source="framework_competitor_agent",
                    title="Placeholder competitor framework",
                    snippet="Basic analysis only. Connect live web intelligence or a dedicated competitor data source for production discovery.",
                    relevance_score=0.35,
                )
            ],
            confidence=0.38,
        )
