# src/superagent/swarm_manager.py
"""
SwarmManager & AgentFactory for MVP.

Responsibilities:
- Map SubTask.type -> concrete Agent class via AgentFactory.
- Execute a Plan (list of SubTask) respecting simple deps.
- Run independent tasks in parallel (ThreadPoolExecutor).
- Return list of SubtaskResult objects (as dict-like).
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional
import logging
from .plan_schema import SubTask, SubtaskResult, Plan
from agentic_report_swarm.agents.research import ResearchAgent
from agentic_report_swarm.agents.trends import TrendsAgent
from agentic_report_swarm.agents.insights import InsightsAgent
from agentic_report_swarm.agents.writer import WriterAgent


logger = logging.getLogger("SwarmManager")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class AgentFactory:
    """
    Minimal factory mapping agent_type -> Agent class.
    Extend this mapping when you add more agent modules.
    """

    def __init__(self, adapters: Optional[Dict[str, object]] = None, memory: Optional[object] = None):
        self.adapters = adapters or {}
        self.memory = memory

    def create(self, agent_type: str):
        # map common subtask types to agent classes
        mapping = {
                "research_overview": ResearchAgent,
                "identify_trends": TrendsAgent,
                "generate_insights": InsightsAgent,
                "write_report": WriterAgent,
        }
        cls = mapping.get(agent_type)
        if cls is None:
            raise ValueError(f"No agent registered for type '{agent_type}'")
        return cls(adapters=self.adapters, memory=self.memory)


class SwarmManager:
    """
    Executes a Plan (list of SubTask). Simple dependency resolution:
    - Repeatedly find tasks whose deps are completed, run them (parallel up to max_workers).
    - Collect SubtaskResult dicts and return them in order of completion.
    """

    def __init__(self, factory: AgentFactory, max_workers: int = 3):
        self.factory = factory
        self.max_workers = max_workers
        self.logger = logger

    def run_subtask(self, subtask: SubTask, context: Optional[Dict] = None) -> SubtaskResult:
        agent = self.factory.create(subtask.type)
        result = agent.run({"id": subtask.id, "type": subtask.type, "payload": subtask.payload}, context=context or {})
        # normalize to SubtaskResult data structure
        return SubtaskResult(
            task_id=result.get("task_id", subtask.id),
            success=bool(result.get("success", False)),
            data=result.get("data", {}),
            message=result.get("message", ""),
            meta=result.get("meta", {})
        )

    def run_plan(self, plan: Plan, context: Optional[Dict] = None) -> List[SubtaskResult]:
        pending: Dict[str, SubTask] = {t.id: t for t in plan.tasks}
        completed: Dict[str, SubtaskResult] = {}
        results: List[SubtaskResult] = []

        # keep looping until no pending tasks
        while pending:
            # find runnable tasks (all deps in completed)
            runnable = []
            for tid, task in list(pending.items()):
                if all(dep in completed for dep in task.deps):
                    runnable.append(task)

            if not runnable:
                # cyclic deps or unmet deps => break to avoid infinite loop
                self.logger.error("No runnable tasks found but pending remains -> possible cyclic deps")
                break

            # execute runnable tasks in parallel
            with ThreadPoolExecutor(max_workers=self.max_workers) as ex:
                future_to_task = {ex.submit(self.run_subtask, t, context): t for t in runnable}
                for fut in as_completed(future_to_task):
                    t = future_to_task[fut]
                    try:
                        res = fut.result()
                        self.logger.info("task %s completed success=%s", t.id, res.success)
                    except Exception as exc:
                        # create failed SubtaskResult
                        res = SubtaskResult(task_id=t.id, success=False, data={}, message=str(exc))
                        self.logger.exception("task %s raised exception", t.id)
                    # mark complete and remove from pending
                    completed[res.task_id] = res
                    results.append(res)
                    if res.task_id in pending:
                        pending.pop(res.task_id, None)

        return results
