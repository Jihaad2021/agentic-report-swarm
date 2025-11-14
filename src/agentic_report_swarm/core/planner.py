# src/superagent/planner.py
"""
Simple rule-based Planner for MVP.
Takes user input -> generates a deterministic Plan with 4 subtasks.
"""

import uuid
from typing import Dict, List
from .plan_schema import Plan, SubTask


class Planner:
    """
    Rule-based MVP Planner.

    Later, this can be replaced by:
    - LLM-based planner
    - JSON-schema-based planning
    - dynamic agent assignment
    """

    def __init__(self):
        pass

    def create_plan(self, user_input: Dict) -> Plan:
        """
        user_input = {
            "topic": "...",
            "context": "...",
            "audience": "...",
            "length": "short" | "detailed"
        }
        """
        plan_id = f"plan-{uuid.uuid4().hex[:8]}"

        topic = user_input.get("topic", "unknown topic")
        length = user_input.get("length", "short")

        tasks: List[SubTask] = []

        # Task 1: Research overview
        tasks.append(SubTask(
            id="t1",
            type="research_overview",
            payload={"topic": topic, "depth": length},
            deps=[]
        ))

        # Task 2: Identify Trends
        tasks.append(SubTask(
            id="t2",
            type="identify_trends",
            payload={"topic": topic, "n_trends": 3},
            deps=[]
        ))

        # Task 3: Generate Insights
        tasks.append(SubTask(
            id="t3",
            type="generate_insights",
            payload={"topic": topic},
            deps=["t1", "t2"]
        ))

        # Task 4: Write Final Report
        tasks.append(SubTask(
            id="t4",
            type="write_report",
            payload={"topic": topic, "length": length},
            deps=["t1", "t2", "t3"]
        ))

        return Plan(plan_id=plan_id, tasks=tasks)
