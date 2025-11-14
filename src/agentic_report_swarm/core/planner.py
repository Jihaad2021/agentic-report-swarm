from .plan_schema import Plan, SubTask
import uuid
from typing import List

def simple_planner(topic: str) -> Plan:
    """
    Rule-based planner that emits 4 subtasks in dependency order:
      - research
      - trends (depends on research)
      - insights (depends on research + trends)
      - writer (depends on insights)
    """
    plan_id = str(uuid.uuid4())
    subtasks: List[SubTask] = [
        SubTask.make(type="research", payload={"topic": topic}, id="t1"),
        SubTask.make(type="trends", payload={"topic": topic}, depends_on=["t1"], id="t2"),
        SubTask.make(type="insights", payload={"topic": topic}, depends_on=["t1", "t2"], id="t3"),
        SubTask.make(type="writer", payload={"topic": topic}, depends_on=["t3"], id="t4"),
    ]
    return Plan(plan_id=plan_id, topic=topic, subtasks=subtasks)
