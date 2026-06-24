"""Analyst agent."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.schemas import AgentName, AgentResult
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span
from multi_agent_research_lab.services.llm_client import LLMClient


class AnalystAgent(BaseAgent):
    """Turns research notes into structured insights."""

    name = "analyst"

    def run(self, state: ResearchState) -> ResearchState:
        if not state.research_notes:
            state.errors.append("Analyst: no research_notes")
            return state

        with trace_span("analyst.run") as span:
            response = LLMClient().complete(
                system_prompt=(
                    "You are an analyst. Extract key claims, compare viewpoints, "
                    "flag weak or conflicting evidence. Be structured."
                ),
                user_prompt=f"Query: {state.request.query}\n\nResearch notes:\n{state.research_notes}",
            )
            state.analysis_notes = response.content
            state.agent_results.append(
                AgentResult(
                    agent=AgentName.ANALYST,
                    content=response.content,
                    metadata={
                        "input_tokens": response.input_tokens,
                        "output_tokens": response.output_tokens,
                        "cost_usd": response.cost_usd,
                    },
                )
            )
        state.add_trace_event(
            "analyst.run",
            {
                "input_tokens": response.input_tokens,
                "output_tokens": response.output_tokens,
                "cost_usd": response.cost_usd,
                "duration_seconds": span["duration_seconds"],
            },
        )
        return state
