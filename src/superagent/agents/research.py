# src/superagent/agents/research.py
from typing import Dict, Any, Optional
from .base import BaseAgent

class ResearchAgent(BaseAgent):
    """
    Minimal ResearchAgent that demonstrates how to extend BaseAgent.
    For now it returns mocked structured data. Later you can replace
    the internal logic to call self.adapters['openai'].call(...) etc.
    """

    def __init__(self, adapters: Optional[Dict[str, Any]] = None, memory: Optional[Any] = None):
        super().__init__(name="ResearchAgent", adapters=adapters, memory=memory)

    def execute_task(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        # payload expected keys: topic, context (optional), depth (optional)
        topic = payload.get("topic", "unknown topic")
        depth = payload.get("depth", "short")

        # If an OpenAI adapter is provided, you would call it here. Example:
        # if "openai" in self.adapters:
        #     prompt = f"Provide a concise market overview of {topic} (depth={depth})"
        #     resp = self.adapters["openai"].call(prompt=prompt, max_tokens=400)
        #     # parse resp into structured output and return
        #     return {"summary": resp["text"], "key_facts": [], "meta": {"tokens": resp.get("tokens", 0)}}

        # For MVP skeleton we return deterministic mock output (easy to test)
        summary = f"(MOCK) Market overview for: {topic} (depth={depth})"
        key_facts = [
            f"Fact 1 about {topic}",
            f"Fact 2 about {topic}"
        ]
        return {
            "summary": summary,
            "key_facts": key_facts,
            "meta": {"tokens": 5}
        }
