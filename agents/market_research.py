from __future__ import annotations

import json

from agents.base import AdkExecutionError, AgentDescriptor, DomainAgent
from rag.vertex_search import MarketRetriever
from shared.schemas import AgentName, EvidenceCitation, ExtractedIdea, MarketResearchOutput


class MarketResearchAgent(DomainAgent):
    descriptor = AgentDescriptor(
        name=AgentName.MARKET_RESEARCH,
        instruction=(
            "Produce evidence-grounded market research for a startup idea. Estimate TAM/SAM/SOM, "
            "growth signals, trends, opportunities, risks, customer segments, buyer personas, "
            "go-to-market signals, and confidence. Prefer cited retrieval evidence."
        ),
        output_schema=MarketResearchOutput,
    )

    def __init__(self, retriever: MarketRetriever) -> None:
        self.retriever = retriever

    async def run(self, idea: ExtractedIdea) -> MarketResearchOutput:
        geography = ", ".join(idea.geographies)
        evidence = await self.retriever.search_market_evidence(
            idea.idea_summary,
            industry=idea.industry,
            geography=geography,
        )

        if self.adk_enabled:
            try:
                return await self._run_with_adk(idea, evidence)
            except (AdkExecutionError, ValueError, json.JSONDecodeError):
                pass

        return self._demo_market_research(idea, evidence)

    async def _run_with_adk(
        self,
        idea: ExtractedIdea,
        evidence: list[EvidenceCitation],
    ) -> MarketResearchOutput:
        prompt = f"""
You are the Market Research specialist for VenturePilot AI.

Return strict JSON matching this schema:
{{
  "tam_usd": "string",
  "sam_usd": "string",
  "som_usd": "string",
  "growth_rate": "string",
  "trends": ["string"],
  "opportunities": ["string"],
  "risks": ["string"],
  "customer_segments": ["string"],
  "buyer_personas": ["string"],
  "go_to_market_signals": ["string"],
  "evidence": [
    {{"source": "string", "title": "string", "snippet": "string", "url": null, "relevance_score": 0.0}}
  ],
  "confidence": 0.0
}}

Startup idea:
{idea.model_dump_json(indent=2)}

Retrieved evidence:
{json.dumps([item.model_dump() for item in evidence], default=str, indent=2)}

Rules:
- Be explicit when estimates are directional.
- Use the evidence supplied; do not invent source URLs.
- Give 3-5 trends, 3-5 opportunities, and 2-4 risks.
- confidence should reflect evidence quality and market specificity.
"""
        payload = await self.run_adk_json(prompt)
        if not payload.get("evidence"):
            payload["evidence"] = [item.model_dump() for item in evidence]
        return MarketResearchOutput.model_validate(payload)

    def _demo_market_research(
        self,
        idea: ExtractedIdea,
        evidence: list[EvidenceCitation],
    ) -> MarketResearchOutput:
        industry = idea.industry.title()
        audience = idea.target_audience
        geography = ", ".join(idea.geographies)
        has_enterprise_motion = any(word in idea.business_model.lower() for word in ["b2b", "saas", "license"])

        if "health" in idea.industry:
            tam, sam, som, growth = "$350B+", "$18B-$45B", "$80M-$250M", "10-16% CAGR in priority software segments"
            risks = ["Long procurement and compliance review cycles", "Clinical workflow integration can slow adoption"]
        elif "fintech" in idea.industry:
            tam, sam, som, growth = "$250B+", "$12B-$35B", "$60M-$180M", "8-14% CAGR depending on regulated niche"
            risks = ["Regulatory scrutiny can increase customer onboarding cost", "Trust and security requirements are high"]
        elif "ai" in idea.industry or "saas" in idea.industry:
            tam, sam, som, growth = "$200B+", "$10B-$28B", "$50M-$160M", "18-30% CAGR in AI-enabled software workflows"
            risks = ["Crowded tooling landscape with fast feature replication", "Accuracy and explainability must be proven early"]
        else:
            tam, sam, som, growth = "$80B+", "$4B-$12B", "$20M-$90M", "7-15% CAGR in comparable software categories"
            risks = ["Category education may be required", "Willingness to pay needs sharper validation"]

        if not has_enterprise_motion:
            risks.append("Business model is not specific enough to forecast sales efficiency")

        return MarketResearchOutput(
            tam_usd=tam,
            sam_usd=sam,
            som_usd=som,
            growth_rate=growth,
            trends=[
                f"Buyers in {industry} are shifting budget toward automation with measurable ROI",
                "AI-assisted research and decision support are moving from experiments into operational workflows",
                "Niche vertical products can win against horizontal platforms when they package domain expertise",
                f"Demand is strongest where {audience} already spend time assembling fragmented evidence",
            ],
            opportunities=[
                f"Start with a narrow {geography} wedge where the pain is frequent and budget owner is clear",
                "Use evidence traceability as a trust differentiator instead of only promising speed",
                "Package pilot outcomes around time saved, higher confidence, and reduced external research spend",
                "Build integrations into the customer systems where validation decisions are already recorded",
            ],
            risks=risks[:4],
            customer_segments=[
                audience,
                "Small teams with high research load and limited analyst capacity",
                "Advisors, operators, or investors who repeatedly compare opportunities",
            ],
            buyer_personas=[
                "Founder or operating lead accountable for go/no-go decisions",
                "Investor analyst seeking faster evidence synthesis",
                "Strategy or innovation manager evaluating new bets",
            ],
            go_to_market_signals=[
                "Concierge pilots should validate the report format before heavy automation",
                "Evidence quality and repeatability are stronger sales assets than raw model novelty",
                "A paid design-partner cohort can expose whether the workflow is urgent or merely interesting",
            ],
            evidence=evidence,
            confidence=0.74 if evidence else 0.56,
        )
