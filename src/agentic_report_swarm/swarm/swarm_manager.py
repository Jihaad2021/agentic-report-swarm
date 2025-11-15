# src/agentic_report_swarm/swarm/swarm_manager.py
from typing import Dict, Any, Optional
from ..core.plan_schema import SubtaskResult
from ..factory.agent_factory import AgentFactory
from .parallel_runner import ParallelRunner
import concurrent.futures
import time

class SwarmManager:
    def __init__(self, agent_factory: AgentFactory, logger=None):
        self.agent_factory = agent_factory
        self.logger = logger

    def _run_agent_safe(self, agent, st):
        """
        Execute agent.run and normalize output. This runs inside worker thread.
        """
        return agent.run({"id": st.id, "type": st.type, "payload": st.payload})

    def execute_plan(self, plan, parallel: bool = False, max_workers: Optional[int] = None, per_task_timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        if not parallel:
            # fallback to the synchronous behavior we had earlier
            return self.execute_plan_sync(plan)
        return self.execute_plan_parallel(plan, max_workers=max_workers, per_task_timeout=per_task_timeout)

    def execute_plan_sync(self, plan) -> Dict[str, Dict[str, Any]]:
        subtasks = {st.id: st for st in plan.subtasks}
        results: Dict[str, Dict[str, Any]] = {}
        pending = set(subtasks.keys())

        while pending:
            progress = False
            for tid in list(pending):
                st = subtasks[tid]
                unmet = [d for d in st.depends_on if d not in results or not results[d].get("success")]
                if unmet:
                    continue
                progress = True
                try:
                    agent = self.agent_factory.build(st.type)
                    out = agent.run({"id": st.id, "type": st.type, "payload": st.payload})
                    results[st.id] = {"id": st.id, "success": True, "output": out}
                except Exception as e:
                    results[st.id] = {"id": st.id, "success": False, "error": str(e)}
                pending.remove(tid)
            if not progress:
                # deadlock or unmet dependencies
                for tid in pending:
                    st = subtasks[tid]
                    unmet = [d for d in st.depends_on if d not in results or not results[d].get("success")]
                    results[tid] = {"id": tid, "success": False, "error": f"unmet_dependencies:{unmet}"}
                break
        return results

    def execute_plan_parallel(self, plan, max_workers: Optional[int] = None, per_task_timeout: Optional[float] = None) -> Dict[str, Dict[str, Any]]:
        subtasks = {st.id: st for st in plan.subtasks}
        results: Dict[str, Dict[str, Any]] = {}
        pending = set(subtasks.keys())
        running: Dict[str, concurrent.futures.Future] = {}
        future_to_tid: Dict[concurrent.futures.Future, str] = {}
        start_times: Dict[str, float] = {}

        with ParallelRunner(max_workers=max_workers) as runner:
            # main loop: submit ready tasks, wait short intervals, check deadlines
            while pending or running:
                # submit ready tasks
                ready = []
                for tid in list(pending):
                    st = subtasks[tid]
                    unmet = [d for d in st.depends_on if d not in results or not results[d].get("success")]
                    if not unmet:
                        ready.append(tid)
                for tid in ready:
                    st = subtasks[tid]
                    agent = self.agent_factory.build(st.type)
                    fut = runner.submit(self._run_agent_safe, agent, st)
                    running[tid] = fut
                    future_to_tid[fut] = tid
                    start_times[tid] = time.monotonic()
                    pending.remove(tid)

                if not running:
                    # nothing to run and pending tasks remain -> deadlock
                    for tid in pending:
                        st = subtasks[tid]
                        unmet = [d for d in st.depends_on if d not in results or not results[d].get("success")]
                        results[tid] = {"id": tid, "success": False, "error": f"unmet_dependencies:{unmet}"}
                    break

                # wait for at least one future to complete or timeout shortly to check deadlines
                done, not_done = ParallelRunner.wait_first(list(running.values()), timeout=0.25)

                # process completed futures
                for fut in list(done):
                    tid = future_to_tid.pop(fut)
                    running.pop(tid, None)
                    start_times.pop(tid, None)
                    try:
                        # no per-task timeout here because we handle timeouts proactively below
                        res = fut.result()
                        results[tid] = {"id": tid, "success": True, "output": res}
                    except Exception as e:
                        results[tid] = {"id": tid, "success": False, "error": str(e)}

                # check running futures for deadline exceed
                if per_task_timeout is not None:
                    now = time.monotonic()
                    for tid in list(running.keys()):
                        st = subtasks[tid]
                        start = start_times.get(tid, now)
                        if (now - start) > per_task_timeout:
                            fut = running.pop(tid)
                            # attempt cancel
                            try:
                                fut.cancel()
                            except Exception:
                                pass
                            # cleanup maps
                            future_to_tid.pop(fut, None)
                            start_times.pop(tid, None)
                            results[tid] = {"id": tid, "success": False, "error": f"timeout after {per_task_timeout}s"}

            # after loop, ensure any still-running futures are awaited/handled
            for tid, fut in list(running.items()):
                try:
                    res = fut.result(timeout=0)
                    results[tid] = {"id": tid, "success": True, "output": res}
                except Exception:
                    results[tid] = {"id": tid, "success": False, "error": "interrupted_or_failed"}

        return results

