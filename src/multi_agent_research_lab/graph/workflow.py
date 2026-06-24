"""LangGraph workflow for multi-agent research."""

from __future__ import annotations

from typing import Literal

from langgraph.graph import END, StateGraph

from multi_agent_research_lab.agents.analyst import AnalystAgent
from multi_agent_research_lab.agents.researcher import ResearcherAgent
from multi_agent_research_lab.agents.supervisor import SupervisorAgent
from multi_agent_research_lab.agents.writer import WriterAgent
from multi_agent_research_lab.core.config import get_settings
from multi_agent_research_lab.core.state import ResearchState

Route = Literal["researcher", "analyst", "writer", "done"]


class MultiAgentWorkflow:
    """Builds and runs the multi-agent graph."""

    def __init__(self) -> None:
        self._supervisor = SupervisorAgent()
        self._agents = {
            "researcher": ResearcherAgent(),
            "analyst": AnalystAgent(),
            "writer": WriterAgent(),
        }

    def _supervisor_node(self, state: ResearchState) -> ResearchState:
        return self._supervisor.run(state)

    def _researcher_node(self, state: ResearchState) -> ResearchState:
        return self._agents["researcher"].run(state)

    def _analyst_node(self, state: ResearchState) -> ResearchState:
        return self._agents["analyst"].run(state)

    def _writer_node(self, state: ResearchState) -> ResearchState:
        return self._agents["writer"].run(state)

    def _route_after_supervisor(self, state: ResearchState) -> Route | str:
        settings = get_settings()
        if state.iteration >= settings.max_iterations:
            return END
        if not state.route_history:
            return END
        route = state.route_history[-1]
        if route == "done":
            return END
        return route  # type: ignore[return-value]

    def build(self) -> object:
        """Compile a LangGraph workflow with supervisor loop."""

        graph = StateGraph(ResearchState)
        graph.add_node("supervisor", self._supervisor_node)
        graph.add_node("researcher", self._researcher_node)
        graph.add_node("analyst", self._analyst_node)
        graph.add_node("writer", self._writer_node)

        graph.set_entry_point("supervisor")
        graph.add_conditional_edges(
            "supervisor",
            self._route_after_supervisor,
            {
                "researcher": "researcher",
                "analyst": "analyst",
                "writer": "writer",
                END: END,
            },
        )
        graph.add_edge("researcher", "supervisor")
        graph.add_edge("analyst", "supervisor")
        graph.add_edge("writer", "supervisor")

        return graph.compile()

    def run(self, state: ResearchState) -> ResearchState:
        """Execute the compiled graph and return final state."""

        graph = self.build()
        result = graph.invoke(state)
        if isinstance(result, ResearchState):
            return result
        return ResearchState.model_validate(result)
