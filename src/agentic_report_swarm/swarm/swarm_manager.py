# src/agentic_report_swarm/swarm/swarm_manager.py
from typing import Dict, Any
from ..core.plan_schema import SubtaskResult
from ..factory.agent_factory import AgentFactory

class SwarmManager:
    """
    Simple synchronous SwarmManager.

    - Accepts an AgentFactory instance (or object exposing .build(agent_type))
    - Executes subtasks when dependencies are met.
    - Returns mapping task_id -> SubtaskResult-like dict.
    """
    def __init__(self, agent_factory: AgentFactory, logger=None):
        self.agent_factory = agent_factory
        self.logger = logger

    def execute_plan(self, plan) -> Dict[str, Dict[str, Any]]:
        """
        Execute the given plan (Plan dataclass) synchronously.

        Returns:
            results: dict keyed by subtask id with {id, success, output?, error?}
        """
        # prepare state
        subtasks = {st.id: st for st in plan.subtasks}
        results: Dict[str, Dict[str, Any]] = {}
        pending = set(subtasks.keys())
        progress = True

        while pending and progress:
            progress = False
            for tid in list(pending):
                st = subtasks[tid]
                # check dependencies
                unmet = [d for d in st.depends_on if d not in results or not results[d].get("success")]
                if unmet:
                    # can't run yet
                    continue
                # execute
                progress = True
                try:
                    agent = self.agent_factory.build(st.type)
                    # agent.run contract expects dict with id/type/payload
                    out = agent.run({"id": st.id, "type": st.type, "payload": st.payload})
                    results[st.id] = {"id": st.id, "success": True, "output": out}
                except Exception as e:
                    results[st.id] = {"id": st.id, "success": False, "error": str(e)}
                pending.remove(tid)

        # if there are still pending tasks -> unmet deps / cycle
        if pending:
            for tid in pending:
                st = subtasks[tid]
                unmet = [d for d in st.depends_on if d not in results or not results[d].get("success")]
                results[tid] = {"id": tid, "success": False, "error": f"unmet_dependencies:{unmet}"}

        return results
