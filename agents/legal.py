from __future__ import annotations

from agents.base import AdkExecutionError, AgentDescriptor, DomainAgent
from shared.schemas import AgentName, EvidenceCitation, ExtractedIdea, LegalAnalysisOutput


class LegalAgent(DomainAgent):
    descriptor = AgentDescriptor(
        name=AgentName.LEGAL,
        instruction=(
            "Identify compliance, privacy, licensing, and geography-specific risks. "
            "This implementation is a framework and not legal advice."
        ),
        output_schema=LegalAnalysisOutput,
    )

    async def run(self, idea: ExtractedIdea) -> LegalAnalysisOutput:
        if self.adk_enabled:
            try:
                return await self._run_with_adk(idea)
            except (AdkExecutionError, ValueError):
                pass
        return self._framework_output(idea)

    async def _run_with_adk(self, idea: ExtractedIdea) -> LegalAnalysisOutput:
        prompt = f"""
Create a preliminary legal and compliance risk framework for this startup idea.

Return JSON only. Required shape:
{{
  "compliance_risks": ["string"],
  "regulations": ["string"],
  "licensing_requirements": ["string"],
  "privacy_concerns": ["string"],
  "geography_specific": {{"Geography": ["string"]}},
  "overall_risk_level": "low|medium|high",
  "evidence": [
    {{"source": "string", "title": "string", "snippet": "string", "url": null, "relevance_score": 0.0}}
  ],
  "confidence": 0.0
}}

Rules:
- This is not legal advice.
- Keep it jurisdiction-aware for the listed geographies.
- Do not invent citations or URLs.
- Mark evidence as framework-level unless a source is supplied.

Startup idea:
{idea.model_dump_json(indent=2)}
"""
        payload = await self.run_adk_json(prompt)
        return LegalAnalysisOutput.model_validate(payload)

    def _framework_output(self, idea: ExtractedIdea) -> LegalAnalysisOutput:
        text = f"{idea.original_description} {idea.industry}".lower()
        privacy = ["Data processing terms and privacy notice alignment"]
        regulations = ["General contract, consumer protection, and advertising compliance"]
        risks = ["Terms should avoid unsupported claims about accuracy or investment outcomes"]
        risk_level = "medium"

        if "health" in text or "patient" in text:
            regulations.extend(["HIPAA in the United States where protected health information is processed"])
            privacy.append("Protected health information handling and business associate agreements")
            risks.append("Clinical or diagnostic claims may trigger stricter review")
            risk_level = "high"
        if "fintech" in text or "investment" in text or "bank" in text:
            regulations.extend(["SEC/FINRA or equivalent financial promotion rules depending on use case"])
            risks.append("Investment recommendations and performance claims require careful boundaries")
            risk_level = "high"
        if "ai" in text:
            regulations.append("Emerging AI governance obligations, including transparency and human oversight")
            privacy.append("Model input retention, training use, and customer data isolation")

        geography_specific = {
            geo: self._geo_notes(geo)
            for geo in idea.geographies
        }

        return LegalAnalysisOutput(
            compliance_risks=risks,
            regulations=regulations,
            licensing_requirements=[
                "Confirm whether the product provides regulated advice or only decision-support information"
            ],
            privacy_concerns=privacy,
            geography_specific=geography_specific,
            overall_risk_level=risk_level,
            evidence=[
                EvidenceCitation(
                    source="framework_legal_agent",
                    title="Preliminary legal framework",
                    snippet="Basic risk screen only. Specialist legal analysis and jurisdiction-specific sources are required for production.",
                    relevance_score=0.32,
                )
            ],
            confidence=0.34,
        )

    def _geo_notes(self, geography: str) -> list[str]:
        normalized = geography.lower()
        if "europe" in normalized or "eu" in normalized:
            return ["Assess GDPR lawful basis, data minimization, DPA terms, and AI Act exposure where applicable"]
        if "united states" in normalized or "us" in normalized:
            return ["Assess federal privacy/security obligations plus state privacy laws such as CCPA/CPRA where applicable"]
        if "australia" in normalized:
            return ["Assess Privacy Act obligations and Australian Consumer Law claim substantiation"]
        return ["Run local counsel review before launch in this geography"]
