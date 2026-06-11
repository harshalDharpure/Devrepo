from __future__ import annotations

from agents.base import AdkExecutionError, AgentDescriptor, DomainAgent
from shared.schemas import AgentName, CompetitorAnalysisOutput, CompetitorRecord, EvidenceCitation, ExtractedIdea


class CompetitorAnalysisAgent(DomainAgent):
    descriptor = AgentDescriptor(
        name=AgentName.COMPETITOR_ANALYSIS,
        instruction=(
            "Map direct and adjacent competitors, saturation, SWOT, and differentiation. "
            "This implementation is intentionally a basic framework pending specialist enrichment."
        ),
        output_schema=CompetitorAnalysisOutput,
    )

    async def run(self, idea: ExtractedIdea) -> CompetitorAnalysisOutput:
        if self.adk_enabled:
            try:
                return await self._run_with_adk(idea)
            except (AdkExecutionError, ValueError):
                pass
        return self._framework_output(idea)

    async def _run_with_adk(self, idea: ExtractedIdea) -> CompetitorAnalysisOutput:
        prompt = f"""
Create a basic competitor-analysis framework for this startup idea.

Return JSON only. Required shape:
{{
  "direct_competitors": [
    {{
      "name": "string",
      "description": "string",
      "pricing": "string",
      "business_model": "string",
      "strengths": ["string"],
      "weaknesses": ["string"]
    }}
  ],
  "market_saturation": "low|medium|high",
  "differentiation_opportunities": ["string"],
  "swot": {{"strengths": ["string"], "weaknesses": ["string"], "opportunities": ["string"], "threats": ["string"]}},
  "evidence": [
    {{"source": "string", "title": "string", "snippet": "string", "url": null, "relevance_score": 0.0}}
  ],
  "confidence": 0.0
}}

Keep this lightweight. Do not claim live web research. Mark evidence as framework-level unless a source is supplied.

Startup idea:
{idea.model_dump_json(indent=2)}
"""
        payload = await self.run_adk_json(prompt)
        return CompetitorAnalysisOutput.model_validate(payload)

    def _framework_output(self, idea: ExtractedIdea) -> CompetitorAnalysisOutput:
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
