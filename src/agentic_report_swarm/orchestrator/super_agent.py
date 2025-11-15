# src/agentic_report_swarm/orchestrator/super_agent.py
from ..core.planner import simple_planner
from ..factory.agent_factory import AgentFactory
from ..swarm.swarm_manager import SwarmManager
from .aggregator import aggregate_to_markdown
from typing import Optional

def run_topic(topic: str, templates: Optional[dict] = None, llm_client=None) -> str:
    """
    Top-level pipeline: plan -> factory -> swarm -> aggregate -> markdown
    """
    plan = simple_planner(topic)
    af = AgentFactory(llm_client=llm_client, templates=templates or {})
    swarm = SwarmManager(agent_factory=af)
    results = swarm.execute_plan(plan)
    md = aggregate_to_markdown(plan, results)
    return md
