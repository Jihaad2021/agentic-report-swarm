# src/agentic_report_swarm/orchestrator/super_agent.py
from ..core.planner import simple_planner
from ..factory.agent_factory import AgentFactory
from ..swarm.swarm_manager import SwarmManager
from typing import Optional

def aggregate_to_markdown(plan, results: dict) -> str:
    """Build a simple markdown report from plan + results (order preserved)."""
    parts = [f"# Research Report — {plan.topic}\n"]
    for st in plan.subtasks:
        parts.append(f"---\n### {st.type} (task {st.id})\n")
        r = results.get(st.id)
        if not r:
            parts.append("_No result_\n")
            continue
        if r.get("success"):
            out = r.get("output") or {}
            text = out.get("text") if isinstance(out, dict) else str(out)
            # fallback: convert whole output to string if no text field
            if not text:
                text = str(out)
            parts.append(f"{text}\n")
        else:
            parts.append(f"**FAILED**: {r.get('error')}\n")
    return "\n".join(parts)

def run_topic(topic: str, templates: Optional[dict] = None, llm_client=None) -> str:
    """
    Top-level pipeline:
      - plan
      - create factory (llm_client + templates)
      - swarm execute
      - aggregate -> markdown string
    """
    # 1. plan
    plan = simple_planner(topic)

    # 2. setup factory (allow injecting llm_client / templates)
    af = AgentFactory(llm_client=llm_client, templates=templates or {})

    # 3. execute via swarm manager
    swarm = SwarmManager(agent_factory=af)
    results = swarm.execute_plan(plan)

    # 4. aggregate
    md = aggregate_to_markdown(plan, results)
    return md
