# src/superagent/agents/trends.py
from typing import Dict, Any, Optional
from ..core.base_agent import BaseAgent

class TrendsAgent(BaseAgent):
    """
    Minimal TrendsAgent: detect mocked trends for a topic.
    """

    def __init__(self, adapters: Optional[Dict[str, Any]] = None, memory: Optional[Any] = None):
        super().__init__(name="TrendsAgent", adapters=adapters, memory=memory)

    def execute_task(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        topic = payload.get("topic", "unknown topic")
        n = int(payload.get("n_trends", 3))
        trends = []
        for i in range(1, n+1):
            trends.append({
                "title": f"(MOCK) Trend {i} for {topic}",
                "explanation": f"Short explanation for trend {i}",
                "confidence": "medium"
            })
        return {"trends": trends, "meta": {"tokens": 4}}
