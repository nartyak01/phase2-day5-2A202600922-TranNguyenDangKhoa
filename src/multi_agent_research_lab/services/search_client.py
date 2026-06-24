"""Search client abstraction for ResearcherAgent."""

import logging

from tavily import TavilyClient

from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.schemas import SourceDocument

logger = logging.getLogger(__name__)

_MOCK_SOURCES = [
    SourceDocument(
        title="GraphRAG: Unlocking LLM discovery on narrative private data",
        url="https://www.microsoft.com/en-us/research/project/graphrag/",
        snippet=(
            "GraphRAG combines knowledge graphs with retrieval-augmented generation "
            "to improve reasoning over large document collections."
        ),
    ),
    SourceDocument(
        title="Retrieval-Augmented Generation for Knowledge-Intensive NLP",
        url="https://arxiv.org/abs/2005.11401",
        snippet=(
            "RAG models retrieve relevant documents and condition generation on them, "
            "reducing hallucination on knowledge-intensive tasks."
        ),
    ),
    SourceDocument(
        title="From Local to Global: A Graph RAG Approach",
        url="https://arxiv.org/abs/2404.16130",
        snippet=(
            "Graph-based RAG builds community summaries over entity graphs "
            "for holistic question answering over text corpora."
        ),
    ),
]


class SearchClient:
    """Provider-agnostic search client with Tavily or mock fallback."""

    def search(self, query: str, max_results: int = 5) -> list[SourceDocument]:
        settings = get_settings()
        if not settings.tavily_api_key:
            logger.warning("TAVILY_API_KEY not set; using mock search sources")
            return _MOCK_SOURCES[:max_results]

        try:
            client = TavilyClient(api_key=settings.tavily_api_key)
            results = client.search(query=query, max_results=max_results)
            documents = [
                SourceDocument(
                    title=r.get("title", "Untitled"),
                    url=r.get("url"),
                    snippet=r.get("content", "")[:500],
                )
                for r in results.get("results", [])
            ]
            return documents or _MOCK_SOURCES[:max_results]
        except Exception as exc:
            logger.warning("Search failed (%s); falling back to mock sources", exc)
            return _MOCK_SOURCES[:max_results]
