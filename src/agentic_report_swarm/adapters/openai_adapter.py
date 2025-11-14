# src/superagent/adapters/openai_adapter.py
"""
Minimal OpenAI adapter skeleton.

- Loads configuration from environment (via os.getenv or python-dotenv).
- Provides `call(prompt, **kwargs)` method that returns a dict:
  {"text": str, "tokens": int, "raw": <raw_response>}
- The actual API call is commented out so this file is safe to commit;
  you can uncomment and implement when you're ready and have keys in .env.
"""

import os
from typing import Any, Dict, Optional

# Optional: enable dotenv when running locally
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

OPENAI_MODEL_DEFAULT = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", None)

class OpenAIAdapter:
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or OPENAI_API_KEY
        self.model = model or OPENAI_MODEL_DEFAULT
        # If you want to initialize real OpenAI client, do it here.
        # Example (uncomment when ready and install openai package):
        #
        # from openai import OpenAI
        # if not self.api_key:
        #     raise ValueError("OpenAI API key is required")
        # self._client = OpenAI(api_key=self.api_key)

    def call(self, prompt: str, max_tokens: int = 400, temperature: float = 0.2, **kwargs) -> Dict[str, Any]:
        """
        Call the LLM and return a standardized dict.
        Currently returns a placeholder dict so this file is safe to commit.
        Replace or uncomment the OpenAI client call when ready.
        """
        # Example real call (pseudocode; uncomment after installing openai and configuring client)
        # resp = self._client.responses.create(model=self.model, input=prompt, max_tokens=max_tokens, temperature=temperature)
        # text = resp.output_text if hasattr(resp, "output_text") else resp["choices"][0]["text"]
        # tokens = getattr(resp, "usage", {}).get("total_tokens", 0)
        # return {"text": text, "tokens": tokens, "raw": resp}

        # Mocked response for skeleton:
        mocked_text = f"(MOCK) Response for prompt: {prompt[:200]}"
        return {"text": mocked_text, "tokens": 3, "raw": None}

# A simple Mock adapter you can use in tests or dev mode
class MockOpenAIAdapter(OpenAIAdapter):
    def __init__(self, canned: Optional[Dict[str, str]] = None):
        super().__init__(api_key="mock", model="mock-model")
        self.canned = canned or {}

    def call(self, prompt: str, **kwargs) -> Dict[str, Any]:
        # try to find a canned response by a simple key in prompt
        for key, resp in self.canned.items():
            if key in prompt:
                return {"text": resp, "tokens": len(resp.split()), "raw": None}
        # fallback
        return {"text": "(MOCK) default response", "tokens": 1, "raw": None}
