from __future__ import annotations

from backend.config import Settings, settings
from shared.schemas import EvidenceCitation


class MarketRetriever:
    async def search_market_evidence(self, query: str, *, industry: str, geography: str) -> list[EvidenceCitation]:
        raise NotImplementedError


class MockMarketRetriever(MarketRetriever):
    async def search_market_evidence(self, query: str, *, industry: str, geography: str) -> list[EvidenceCitation]:
        region = geography or "target geography"
        topic = industry or "startup market"
        return [
            EvidenceCitation(
                source="mock_market_rag",
                title=f"{topic.title()} market expansion signals in {region}",
                snippet=(
                    f"Demo retrieval indicates rising buyer demand, active investor interest, "
                    f"and fragmented vendor coverage for {topic} in {region}."
                ),
                relevance_score=0.82,
            ),
            EvidenceCitation(
                source="mock_market_rag",
                title=f"{topic.title()} adoption and budget pressure",
                snippet=(
                    "Demo evidence highlights procurement pressure for automation, measurable ROI, "
                    "and tools that reduce manual research time."
                ),
                relevance_score=0.76,
            ),
            EvidenceCitation(
                source="mock_market_rag",
                title=f"{topic.title()} go-to-market benchmarks",
                snippet=(
                    "Comparable SaaS categories typically validate demand through niche segments, "
                    "expert-led pilots, and integration-led distribution."
                ),
                relevance_score=0.71,
            ),
        ]


class VertexAISearchRetriever(MarketRetriever):
    """Vertex AI Search adapter using Discovery Engine serving configs."""

    def __init__(self, config: Settings = settings) -> None:
        self.config = config

    async def search_market_evidence(self, query: str, *, industry: str, geography: str) -> list[EvidenceCitation]:
        try:
            from google.cloud import discoveryengine_v1 as discoveryengine
        except ImportError:
            return []

        if not (
            self.config.google_cloud_project
            and self.config.vertex_search_data_store
            and not self.config.use_mock_retrieval
        ):
            return []

        client = discoveryengine.SearchServiceClient()
        serving_config = client.serving_config_path(
            project=self.config.google_cloud_project,
            location=self.config.vertex_search_location,
            data_store=self.config.vertex_search_data_store,
            serving_config="default_search",
        )
        request = discoveryengine.SearchRequest(
            serving_config=serving_config,
            query=f"{query} {industry} {geography} market size growth TAM",
            page_size=5,
        )
        response = client.search(request)

        citations: list[EvidenceCitation] = []
        for index, result in enumerate(response.results):
            document = result.document
            struct_data = dict(document.struct_data or {})
            title = str(struct_data.get("title") or document.name.rsplit("/", 1)[-1])
            snippet = str(
                struct_data.get("snippet")
                or struct_data.get("description")
                or "Vertex AI Search result matched the market research query."
            )
            url = struct_data.get("uri") or struct_data.get("url")
            citations.append(
                EvidenceCitation(
                    source="vertex_ai_search",
                    title=title,
                    snippet=snippet[:500],
                    url=str(url) if url else None,
                    relevance_score=max(0.2, 0.9 - index * 0.08),
                )
            )
        return citations


def build_market_retriever(config: Settings = settings) -> MarketRetriever:
    if config.use_mock_retrieval:
        return MockMarketRetriever()
    return VertexAISearchRetriever(config)

