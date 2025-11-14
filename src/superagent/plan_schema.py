# src/superagent/plan_schema.py
"""
Dataclasses and schemas for Plan, SubTask, and SubtaskResult.
Used by Planner, SuperAgent, and SwarmManager.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class SubTask:
    id: str
    type: str
    payload: Dict
    deps: List[str] = field(default_factory=list)
    timeout: Optional[int] = 60   # seconds


@dataclass
class Plan:
    plan_id: str
    tasks: List[SubTask]


@dataclass
class SubtaskResult:
    task_id: str
    success: bool
    data: Dict
    message: str = ""
    meta: Dict = field(default_factory=dict)
