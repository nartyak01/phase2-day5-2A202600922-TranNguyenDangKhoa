"""Supervisor / router."""

from multi_agent_research_lab.agents.base import BaseAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState
from multi_agent_research_lab.observability.tracing import trace_span


class SupervisorAgent(BaseAgent):
    """Decides which worker should run next and when to stop."""

    name = "supervisor"

    def run(self, state: ResearchState) -> ResearchState:
        settings = get_settings()

        with trace_span("supervisor.route", {"iteration": state.iteration}) as span:
            if state.iteration >= settings.max_iterations:
                route = "done"
            elif not state.research_notes:
                route = "researcher"
            elif not state.analysis_notes:
                route = "analyst"
            elif not state.final_answer:
                route = "writer"
            else:
                route = "done"

            state.record_route(route)
            state.add_trace_event(
                "supervisor.route",
                {
                    "route": route,
                    "iteration": state.iteration,
                    "duration_seconds": span["duration_seconds"],
                },
            )
        return state
