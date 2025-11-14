# src/agentic_report_swarm/utils/llm_client.py
from typing import Any, Dict, Optional
import os

# Try to import a real adapter if provided by adapters package
try:
    from ..adapters.openai_adapter import RealOpenAIAdapter, MockOpenAIAdapter
except Exception:
    # fallback minimal mock if adapters package missing
    RealOpenAIAdapter = None
    class MockOpenAIAdapter:
        def generate(self, prompt: str, **kwargs) -> str:
            return f"[MOCK-ADAPTER] Generated for: {prompt}"

class LLMClient:
    """
    High-level LLM client facade.
    Use `LLMClient.from_env()` to auto-select adapter (mock by default).
    """

    def __init__(self, adapter):
        self.adapter = adapter

    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from prompt. kwargs passed to adapter.
        """
        return self.adapter.generate(prompt, **kwargs)

    @staticmethod
    def from_env(api_key_env: Optional[str] = "OPENAI_API_KEY", prefer_real: bool = False):
        """
        Create LLMClient using environment / preference.
        prefer_real=True will attempt to create RealOpenAIAdapter and raise
        helpful error if not possible.
        """
        api_key = os.environ.get(api_key_env)
        if prefer_real:
            if RealOpenAIAdapter is None:
                raise RuntimeError("RealOpenAIAdapter not available. Install adapters or implement RealOpenAIAdapter.")
            return LLMClient(RealOpenAIAdapter(api_key=api_key))
        # default to mock adapter
        return LLMClient(MockOpenAIAdapter())
