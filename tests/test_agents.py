# tests/test_agents.py
from agentic_report_swarm.factory.agent_factory import AgentFactory
from agentic_report_swarm.utils.llm_client import LLMClient
from agentic_report_swarm.adapters.openai_adapter import MockOpenAIAdapter

def test_generic_agent_with_mock_llm():
    adapter = MockOpenAIAdapter()
    client = LLMClient(adapter)
    factory = AgentFactory(llm_client=client, templates={"research": {"prompt": "Research about {task[payload][topic]}"}})
    agent = factory.build("research")
    task = {"id": "t1", "type": "research", "payload": {"topic": "quantum computing"}}
    res = agent.run(task)
    assert "MOCK-ADAPTER" in res["text"] or "Generated for" in res["text"]
    assert res["meta"]["task_id"] == "t1"
