from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import uuid

@dataclass
class SubTask:
    id: str
    type: str
    payload: Dict[str, Any]
    depends_on: List[str] = field(default_factory=list)

    @staticmethod
    def make(type: str, payload: Dict[str, Any], depends_on: Optional[List[str]] = None, id: Optional[str] = None):
        return SubTask(
            id=id or str(uuid.uuid4()),
            type=type,
            payload=payload,
            depends_on=depends_on or []
        )

    def to_dict(self):
        return asdict(self)

@dataclass
class Plan:
    plan_id: str
    topic: str
    subtasks: List[SubTask] = field(default_factory=list)

    @staticmethod
    def create_for_topic(topic: str):
        import uuid
        return Plan(plan_id=str(uuid.uuid4()), topic=topic, subtasks=[])

    def to_dict(self):
        return {
            "plan_id": self.plan_id,
            "topic": self.topic,
            "subtasks": [st.to_dict() for st in self.subtasks],
        }

@dataclass
class SubtaskResult:
    id: str
    success: bool
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self):
        return asdict(self)
