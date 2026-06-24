"""Researcher agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient
from multi_agent_research_lab.services.search_client import SearchClient


class ResearcherAgent(BaseAgent):
    """Collects sources and creates concise research notes."""

    name = "researcher"

    def run(self, state: ResearchState) -> ResearchState:
        with trace_span("researcher.run", {"query": state.request.query}) as span:
            search = SearchClient()
            llm = LLMClient()
            sources = search.search(state.request.query, state.request.max_sources)
            state.sources = sources
            sources_text = "\n\n".join(
                f"[{i + 1}] {s.title}\n{s.snippet}\nURL: {s.url}" for i, s in enumerate(sources)
            )
            response = llm.complete(
                system_prompt=(
                    "You are a research assistant. Summarize sources into concise "
                    "research notes with citations [1], [2]..."
                ),
                user_prompt=f"Query: {state.request.query}\n\nSources:\n{sources_text}",
            )
            state.research_notes = response.content
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.RESEARCHER,
                    content=response.content,
                    metadata={
                        "num_sources": len(sources),
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                    },
                )
            )
        state.add_trace_event(
            "researcher.run",
            {
                "sources": len(state.sources),
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
                "duration_seconds": span["duration_seconds"],
            },
        )
        return state
