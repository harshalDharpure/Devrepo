from __future__ import annotations

import re

from agents.base import AgentDescriptor, DomainAgent
from shared.schemas import AgentName, ExtractedIdea


class FrontDeskAgent(DomainAgent):
    descriptor = AgentDescriptor(
        name=AgentName.FRONT_DESK,
        instruction=(
            "Validate startup idea quality, extract industry, customer, geography, "
            "business model, and ask concise clarification questions when the idea is underspecified."
        ),
    )

    async def run(self, description: str, clarifications: dict[str, str] | None = None) -> ExtractedIdea:
        merged = description.strip()
        if clarifications:
            merged = f"{merged}\nClarifications: {clarifications}"

        lowered = merged.lower()
        geographies = self._extract_geographies(lowered)
        industry = self._extract_industry(lowered)
        audience = self._extract_audience(merged)
        business_model = self._extract_business_model(lowered)
        pricing = self._extract_pricing(merged)
        keywords = self._keywords(merged)

        missing = []
        if len(merged) < 80:
            missing.append("Describe the target customer and the painful workflow in one or two sentences.")
        if audience == "early adopters":
            missing.append("Who is the first paying customer segment?")
        if business_model == "unknown":
            missing.append("What is the business model or expected pricing motion?")

        quality_score = min(1.0, max(0.25, len(merged) / 450))
        if audience != "early adopters":
            quality_score += 0.12
        if geographies:
            quality_score += 0.08
        if business_model != "unknown":
            quality_score += 0.1
        quality_score = min(1.0, quality_score)

        summary = re.sub(r"\s+", " ", description.strip())
        if len(summary) > 220:
            summary = f"{summary[:217].rstrip()}..."

        return ExtractedIdea(
            original_description=description,
            idea_summary=summary,
            industry=industry,
            target_audience=audience,
            business_model=business_model,
            geographies=geographies or ["United States"],
            pricing=pricing,
            keywords=keywords,
            quality_score=quality_score,
            needs_clarification=quality_score < 0.45,
            clarification_questions=missing[:3],
        )

    def _extract_geographies(self, text: str) -> list[str]:
        matches: list[str] = []
        checks = {
            "United States": ["us", "u.s.", "usa", "united states", "america"],
            "European Union": ["eu", "europe", "european union"],
            "Australia": ["australia", "anz"],
            "United Kingdom": ["uk", "u.k.", "united kingdom"],
            "Canada": ["canada"],
            "Global": ["global", "worldwide"],
        }
        for label, needles in checks.items():
            if any(f" {needle} " in f" {text} " for needle in needles):
                matches.append(label)
        return matches

    def _extract_industry(self, text: str) -> str:
        industry_terms = [
            "healthcare",
            "fintech",
            "legaltech",
            "edtech",
            "climate",
            "cybersecurity",
            "ai",
            "devtools",
            "ecommerce",
            "marketplace",
            "saas",
        ]
        for term in industry_terms:
            if term in text:
                return term
        return "software"

    def _extract_audience(self, text: str) -> str:
        patterns = [
            r"target audience is ([^.]+)",
            r"for ([^.]+?)(?:\.|,| with | using )",
            r"serves ([^.]+)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, flags=re.IGNORECASE)
            if match:
                return match.group(1).strip()[:140]
        return "early adopters"

    def _extract_business_model(self, text: str) -> str:
        if "saas" in text:
            return "B2B SaaS" if "b2b" in text else "SaaS"
        if "marketplace" in text:
            return "marketplace"
        if "subscription" in text:
            return "subscription"
        if "usage" in text or "pay as you go" in text:
            return "usage-based"
        if "license" in text:
            return "licensing"
        return "unknown"

    def _extract_pricing(self, text: str) -> str | None:
        match = re.search(r"\$[\d,]+(?:\s*-\s*\$?[\d,]+)?(?:/[a-z]+)?", text, flags=re.IGNORECASE)
        return match.group(0) if match else None

    def _keywords(self, text: str) -> list[str]:
        words = re.findall(r"[A-Za-z][A-Za-z0-9+-]{2,}", text.lower())
        stop = {"the", "and", "for", "using", "with", "that", "this", "from", "are", "is", "target"}
        unique = []
        for word in words:
            if word not in stop and word not in unique:
                unique.append(word)
        return unique[:12]

