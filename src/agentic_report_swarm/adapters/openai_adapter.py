# src/agentic_report_swarm/adapters/openai_adapter.py
import os

class MockOpenAIAdapter:
    def generate(self, prompt: str, **kwargs) -> str:
        return f"[MOCK-ADAPTER] Generated for: {prompt}"

class RealOpenAIAdapter:
    """
    Minimal wrapper around openai python package.
    If `openai` package is not installed, import will fail at runtime with
    a clear error message. This adapter expects an `api_key` argument or the
    OPENAI_API_KEY env var.
    """
    def __init__(self, api_key: str = None, model: str = "gpt-4o-mini"):
        try:
            import openai  # type: ignore
        except Exception as e:
            raise RuntimeError("openai package not installed. Install `openai` to use RealOpenAIAdapter.") from e
        self.openai = openai
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY not set. Provide api_key to RealOpenAIAdapter or set env var.")
        self.openai.api_key = self.api_key
        self.model = model

    def generate(self, prompt: str, **kwargs) -> str:
        # synchronous completion call (simple). You can replace with streaming.
        resp = self.openai.Completion.create(engine=self.model, prompt=prompt, max_tokens=512, **kwargs)
        # adapt depending on response shape (this is a minimal example)
        choices = resp.get("choices") or []
        if choices:
            return choices[0].get("text", "").strip()
        return ""
