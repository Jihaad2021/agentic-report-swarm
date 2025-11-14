"""
src/superagent/agents/base.py

BaseAgent - abstract base class for all SubAgents in Agentic Report Swarm.

Responsibilities:
- Define a clear interface (`execute`) that concrete agents must implement.
- Provide common utilities: logging, adapters/memory injection, basic error handling,
  result normalization, health-check and lifecycle stubs.
- Keep implementation LLM-agnostic; agents should use injected adapters for OpenAI calls.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging
import time

DEFAULT_TIMEOUT_SECONDS = 60


class BaseAgent(ABC):
    """
    Abstract base for all agents.

    Concrete agents must implement `execute_task` which receives a task payload and
    an execution context (both are plain dictionaries). The agent `run` wrapper
    handles timing, logging, exception capture, and standardized result shape.

    Attributes:
        name: human-readable agent name (e.g., "ResearchAgent")
        adapters: optional dictionary of external adapters (e.g., {"openai": OpenAIAdapter(...)})
        memory: optional small key-value store object implementing .get/.set (injected)
        logger: per-agent logger
        timeout: soft timeout in seconds for run() (enforced only at wrapper level)
    """

    def __init__(
        self,
        name: str,
        adapters: Optional[Dict[str, Any]] = None,
        memory: Optional[Any] = None,
        timeout: int = DEFAULT_TIMEOUT_SECONDS,
    ):
        self.name = name
        self.adapters = adapters or {}
        self.memory = memory
        self.timeout = timeout
        self.logger = logging.getLogger(f"agent.{self.name}")
        # default logger level can be controlled by app config; set INFO for minimal verbosity
        if not self.logger.handlers:
            # avoid adding multiple handlers if logger is configured elsewhere
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    # --- lifecycle / utility methods ------------------------------------------------

    def health_check(self) -> Dict[str, Any]:
        """
        Lightweight health check for the agent.
        Override if agent needs to probe adapters or external services.
        Returns a dict with at least {"ok": bool, "details": ...}
        """
        try:
            # by default we just return basic info
            return {"ok": True, "agent": self.name}
        except Exception as exc:  # pragma: no cover - generic fallback
            return {"ok": False, "error": str(exc)}

    def terminate(self) -> None:
        """
        Hook to clean up resources (open files, connections). Override if needed.
        """
        self.logger.debug("terminate called for agent %s", self.name)
        # default: nothing to do

    # --- run wrapper (standardizes result shape & logging) ---------------------------

    def run(self, task: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Wrapper method to execute a subtask and return standardized result.

        Args:
            task: dict describing the subtask (e.g., {"id": "t1", "type": "research_overview", "payload": {...}})
            context: optional shared context (from SuperAgent / Memory)

        Returns:
            A standardized dict:
            {
                "task_id": str,
                "success": bool,
                "data": dict,         # agent-specific structured output
                "message": str,       # optional human readable message
                "meta": {             # tokens, duration_ms, agent name, etc.
                    "agent": self.name,
                    "duration_ms": int,
                    ...
                }
            }
        """
        start_ts = time.time()
        task_id = task.get("id", "<no-id>")
        context = context or {}
        self.logger.info("starting task_id=%s type=%s", task_id, task.get("type"))

        try:
            result_data = self.execute_task(task.get("payload", {}), context)
            success = True
            message = result_data.get("message", "") if isinstance(result_data, dict) else ""
        except Exception as exc:  # agent implementer should raise explicit exceptions when needed
            self.logger.exception("agent %s failed on task %s", self.name, task_id)
            result_data = {}
            success = False
            message = str(exc)

        duration_ms = int((time.time() - start_ts) * 1000)
        meta = {"agent": self.name, "duration_ms": duration_ms}

        # Allow concrete result to include meta (e.g., tokens). Merge if present.
        if isinstance(result_data, dict) and "meta" in result_data:
            meta.update(result_data.pop("meta"))

        standardized = {
            "task_id": task_id,
            "success": success,
            "data": result_data if isinstance(result_data, dict) else {"result": result_data},
            "message": message,
            "meta": meta,
        }

        self.logger.info("finished task_id=%s success=%s duration_ms=%d", task_id, success, duration_ms)
        return standardized

    # --- core contract for concrete agents -----------------------------------------

    @abstractmethod
    def execute_task(self, payload: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Concrete agents must implement this method.

        Args:
            payload: subtask-specific inputs
            context: shared context (memory, previous results, config)

        Returns:
            Structured dict representing the agent's output. Example:
            {
                "summary": "...",
                "key_facts": [...],
                "meta": {"tokens": 120}
            }

        Note: this method should NOT catch all exceptions silently. Let exceptions bubble
        to `run()` so they are logged/normalized there.
        """
        raise NotImplementedError
