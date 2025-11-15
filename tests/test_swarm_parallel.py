# tests/test_swarm_parallel.py
import time
from agentic_report_swarm.swarm.swarm_manager import SwarmManager
from agentic_report_swarm.core.plan_schema import Plan, SubTask
from agentic_report_swarm.factory.agent_factory import AgentFactory
from agentic_report_swarm.core.base_agent import BaseAgent

# Simple SleepAgent used for testing parallelism
class SleepAgent(BaseAgent):
    def __init__(self, name, sleep_for=1.0):
        super().__init__(name)
        self.sleep_for = sleep_for

    def run(self, task):
        time.sleep(self.sleep_for)
        return {"text": f"slept {self.sleep_for}", "meta": {"agent": self.name}}

# Custom AgentFactory that returns SleepAgent instances with configured durations
class SleepAgentFactory:
    def __init__(self, durations: dict):
        """
        durations: dict mapping agent_type -> sleep seconds
        """
        self.durations = durations

    def build(self, agent_type: str):
        dur = self.durations.get(agent_type, 1.0)
        return SleepAgent(name=f"{agent_type}_agent", sleep_for=dur)

def make_plan_independent():
    p = Plan(plan_id="p-par", topic="parallel-test", subtasks=[
        SubTask(id="t1", type="a", payload={}),
        SubTask(id="t2", type="b", payload={}),
        SubTask(id="t3", type="c", payload={}),
    ])
    return p

def test_parallel_runner_speeds_up():
    # three tasks, each sleeps 1.0s -> if serial would be ~3s; parallel should be ~1s
    durations = {"a": 1.0, "b": 1.0, "c": 1.0}
    af = SleepAgentFactory(durations)
    sm = SwarmManager(agent_factory=af)
    plan = make_plan_independent()
    start = time.monotonic()
    results = sm.execute_plan(plan, parallel=True, max_workers=3, per_task_timeout=5.0)
    elapsed = time.monotonic() - start

    assert all(r["success"] for r in results.values())
    # parallel should be significantly faster than serial; allow some slack
    assert elapsed < 2.0, f"expected parallel <2s but got {elapsed:.2f}s"

def test_parallel_task_timeout():
    durations = {"a": 0.1, "b": 5.0}  # b will timeout
    af = SleepAgentFactory(durations)
    sm = SwarmManager(agent_factory=af)
    # plan: a and b independent
    p = Plan(plan_id="p-timeout", topic="t", subtasks=[
        SubTask(id="t1", type="a", payload={}),
        SubTask(id="t2", type="b", payload={}),
    ])
    results = sm.execute_plan(p, parallel=True, max_workers=2, per_task_timeout=1.0)
    assert results["t1"]["success"] is True
    assert results["t2"]["success"] is False
    assert "timeout" in results["t2"]["error"]
