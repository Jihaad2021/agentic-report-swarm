# tests/test_research_agent.py
import pytest
from agentic_report_swarm.agents.research_agent import ResearchAgent
from agentic_report_swarm.adapters.openai_adapter import MockOpenAIAdapter

def test_research_agent_returns_structure():
    # create a mock adapter with a canned response (not used by current ResearchAgent but demonstrates injection)
    canned = {"Market overview": "This is a mocked market overview."}
    mock_adapter = MockOpenAIAdapter(canned=canned)

    # instantiate agent with adapters (optional)
    agent = ResearchAgent(adapters={"openai": mock_adapter})

    task = {"id": "t1", "type": "research_overview", "payload": {"topic": "e-commerce fashion Indonesia Q4", "depth": "short"}}
    res = agent.run(task, context={})

    assert isinstance(res, dict)
    assert res["task_id"] == "t1"
    assert "success" in res
    assert res["success"] is True
    assert "data" in res and "summary" in res["data"]
    assert isinstance(res["data"]["key_facts"], list)
    assert res["meta"]["agent"] == "ResearchAgent"
