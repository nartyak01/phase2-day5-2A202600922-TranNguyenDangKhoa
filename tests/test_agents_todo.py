import pytest

from multi_agent_research_lab.agents import SupervisorAgent
from multi_agent_research_lab.core.schemas import ResearchQuery
from multi_agent_research_lab.core.state import ResearchState


def test_supervisor_routes_to_researcher_first() -> None:
    state = ResearchState(request=ResearchQuery(query="Explain multi-agent systems"))
    result = SupervisorAgent().run(state)
    assert result.route_history[-1] == "researcher"


def test_supervisor_routes_to_done_when_complete() -> None:
    state = ResearchState(
        request=ResearchQuery(query="Explain multi-agent systems"),
        research_notes="notes",
        analysis_notes="analysis",
        final_answer="answer",
    )
    result = SupervisorAgent().run(state)
    assert result.route_history[-1] == "done"
