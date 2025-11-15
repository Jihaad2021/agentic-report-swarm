# tests/test_agent_schema_validation.py
from agentic_report_swarm.agents.generic_agent import GenericAgent
from agentic_report_swarm.utils.llm_client import LLMClient

class MockLLMReturningJSON:
    def __init__(self, text: str):
        self.text = text
    def generate(self, prompt: str) -> str:
        return self.text

def test_agent_validates_json_success():
    # Create payload matching ResearchResult schema
    json_text = '{"title": "X", "key_facts": ["a","b","c"], "sources": ["s1","s2"]}'
    client = LLMClient(MockLLMReturningJSON(json_text))
    agent = GenericAgent(name="research_agent", llm_client=client, template={"prompt": "ignore"})
    res = agent.run({"id": "t1", "type": "research", "payload": {"topic": "x"}})
    assert "json" in res
    assert res.get("validated") is True
    assert "validated_data" in res

def test_agent_validation_error_recorded():
    # Missing required fields for ResearchResult
    bad_json = '{"title": "bad"}'
    client = LLMClient(MockLLMReturningJSON(bad_json))
    agent = GenericAgent(name="research_agent", llm_client=client, template={"prompt": "ignore"})
    res = agent.run({"id": "t2", "type": "research", "payload": {"topic": "x"}})
    assert "json" in res
    assert res.get("validated") is False
    assert "validation_error" in res
