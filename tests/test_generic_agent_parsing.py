# tests/test_generic_agent_parsing.py
from agentic_report_swarm.agents.generic_agent import GenericAgent

class JSONMockLLM:
    def __init__(self, payload: str):
        self.payload = payload
    def generate(self, prompt: str) -> str:
        # ignore prompt, return provided payload
        return self.payload

def test_generic_agent_parses_json_direct():
    payload = '{"title": "Test", "score": 9}'
    client = JSONMockLLM(payload)
    agent = GenericAgent(name="g", llm_client=client, template={"prompt": "ignore"})
    res = agent.run({"id": "t1", "type": "research", "payload": {"topic": "x"}})
    assert "json" in res
    assert isinstance(res["json"], dict)
    assert res["json"]["title"] == "Test"

def test_generic_agent_parses_json_in_codeblock():
    payload = "Some text\n```json\n{\"a\": 2}\n```\nmore text"
    client = JSONMockLLM(payload)
    agent = GenericAgent(name="g", llm_client=client, template={"prompt": "ignore"})
    res = agent.run({"id": "t2", "type": "insights", "payload": {"topic": "y"}})
    assert "json" in res
    assert res["json"]["a"] == 2
