# src/superagent/superagent.py
"""
SuperAgent orchestrator (MVP).

Flow:
- receive user command dict
- create plan via Planner
- create AgentFactory & SwarmManager (inject adapters / memory)
- run plan => list of SubtaskResult
- aggregate results => markdown
- persist markdown to demos/example_reports/report-<plan_id>.md
- return dict with metadata (path, plan_id)
"""

import os
import uuid
from typing import Dict, Any
from .planner import Planner
from .swarm_manager import AgentFactory, SwarmManager
from .aggregator import aggregate_results
from agentic_report_swarm.adapters.openai_adapter import MockOpenAIAdapter, OpenAIAdapter

DEMO_REPORT_DIR = os.path.join(os.getcwd(), "demos", "example_reports")
os.makedirs(DEMO_REPORT_DIR, exist_ok=True)


class SuperAgent:
    def __init__(self, adapters: Dict[str, Any] = None, memory: Any = None, max_workers: int = 3):
        self.adapters = adapters or {}
        self.memory = memory
        self.planner = Planner()
        self.factory = AgentFactory(adapters=self.adapters, memory=self.memory)
        self.manager = SwarmManager(factory=self.factory, max_workers=max_workers)

    def run(self, command: Dict[str, Any], save: bool = True) -> Dict[str, Any]:
        """
        command: {
            "topic": str,
            "context": str (optional),
            "audience": str (optional),
            "length": "short" | "detailed"
        }
        """
        # 1. plan
        plan = self.planner.create_plan(command)

        # 2. run swarm
        results = self.manager.run_plan(plan, context={"user": command})

        # 3. aggregate
        metadata = {"plan_id": plan.plan_id, "topic": command.get("topic", ""), "n_tasks": len(plan.tasks)}
        agg = aggregate_results(results, plan, metadata=metadata)
        markdown = agg.get("markdown", "")

        # 4. persist
        report_filename = f"report-{plan.plan_id}.md"
        report_path = os.path.join(DEMO_REPORT_DIR, report_filename)
        if save:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(markdown)

        return {"plan_id": plan.plan_id, "report_path": report_path, "markdown": markdown, "results": [r.__dict__ for r in results], "meta": metadata}
