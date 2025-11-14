from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """
    BaseAgent defines the minimal interface every agent must implement.
    Concrete agents should override `run(task)` and return a serializable dict.
    """

    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}

    @abstractmethod
    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the task and return a dict result, e.g. {"text": "...", "meta": {...}}.
        """
        raise NotImplementedError()

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"
