# src/superagent/agents/writer.py
from typing import Dict, Any, Optional
from ..core.base_agent import BaseAgent

class WriterAgent(BaseAgent):
    """
    Minimal WriterAgent: assemble a final markdown report.
    In real flow it will accept partial results passed via context or aggregator;
    for skeleton it returns a deterministic markdown text.
    """

    def __init__(self, adapters: Optional[Dict[str, Any]] = None, memory: Optional[Any] = None):
        super().__init__(name="WriterAgent", adapters=adapters, memory=memory)

    def execute_task(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        length = payload.get("length", "short")
        topic = payload.get("topic", "unknown topic")
        md = f"# Report: {topic}\n\n## Executive Summary\n(MOCK) Executive summary for {topic} (length={length})\n\n## Trends\n- Trend 1\n- Trend 2\n\n## Insights\n- Insight A\n- Insight B\n\n## Recommendations\n- Recommendation 1\n"
        return {"markdown": md, "meta": {"tokens": 8}}
