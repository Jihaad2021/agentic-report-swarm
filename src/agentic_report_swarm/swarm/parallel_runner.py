# src/agentic_report_swarm/swarm/parallel_runner.py
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from typing import Callable, Any, Dict, Optional
import concurrent.futures

class ParallelRunner:
    """
    Thin wrapper around ThreadPoolExecutor providing a small convenience API.
    We keep it simple: user will call executor.submit(...) directly.
    """
    def __init__(self, max_workers: Optional[int] = None):
        self.max_workers = max_workers or None
        self._executor: Optional[ThreadPoolExecutor] = None

    def __enter__(self):
        self._executor = ThreadPoolExecutor(max_workers=self.max_workers)
        return self

    def __exit__(self, exc_type, exc, tb):
        if self._executor:
            self._executor.shutdown(wait=True)

    def submit(self, fn: Callable, *args, **kwargs):
        if not self._executor:
            raise RuntimeError("ParallelRunner context not entered")
        return self._executor.submit(fn, *args, **kwargs)

    @staticmethod
    def wait_first(futures, timeout=None):
        """
        Wait until at least one future is done, then return (done, not_done).
        """
        done, not_done = wait(futures, return_when=FIRST_COMPLETED, timeout=timeout)
        return done, not_done
