"""Writer agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient


class WriterAgent(BaseAgent):
    """Produces final answer from research and analysis notes."""

    name = "writer"

    def run(self, state: ResearchState) -> ResearchState:
        if not state.analysis_notes:
            state.errors.append("Writer: no analysis_notes")
            return state

        with trace_span("writer.run") as span:
            sources_ref = "\n".join(f"- {s.title}: {s.url}" for s in state.sources)
            response = LLMClient().complete(
                system_prompt=(
                    f"Write a clear final answer for audience: {state.request.audience}. "
                    "Include citations. Target ~500 words if the query asks for it."
                ),
                user_prompt=(
                    f"Query: {state.request.query}\n\n"
                    f"Analysis:\n{state.analysis_notes}\n\n"
                    f"Sources:\n{sources_ref}"
                ),
            )
            state.final_answer = response.content
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.WRITER,
                    content=response.content,
                    metadata={
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                    },
                )
            )
        state.add_trace_event(
            "writer.run",
            {
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
                "duration_seconds": span["duration_seconds"],
            },
        )
        return state
