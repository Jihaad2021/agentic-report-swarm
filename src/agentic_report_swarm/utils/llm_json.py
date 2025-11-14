# src/agentic_report_swarm/utils/llm_json.py
"""
Robust JSON extraction/parsing helpers for LLM outputs.

Functions:
- parse_maybe_json(text: str) -> Union[dict, list, str]
    Try to extract JSON from text; return parsed object if found, else original text.

Notes:
- Heuristics are intentionally conservative: prefer returning parsed JSON only when
  json.loads succeeds.
- This module is not a full HTML/markdown parser — it's a pragmatic utility for
  common LLM outputs patterns (plain JSON, JSON in triple-backticks, extra commentary).
"""
import json
import re
from typing import Any, Union, Optional


def safe_json_loads(s: str) -> Optional[Any]:
    """Attempt to json.loads(s) with basic cleanups. Return parsed object or None."""
    if not isinstance(s, str):
        return None
    s = s.strip()
    if not s:
        return None

    # Try directly
    try:
        return json.loads(s)
    except Exception:
        pass

    # Common fixes: single quotes -> double quotes (naive), trailing commas removal
    try:
        cand = s.replace("'", '"')
        # remove trailing commas before closing braces/brackets: "a":1,}
        cand = re.sub(r',\s*([\]\}])', r'\1', cand)
        return json.loads(cand)
    except Exception:
        pass

    return None


def extract_code_blocks(text: str) -> list:
    """
    Find triple-backtick blocks and return list of their contents (without backticks).
    Returns empty list if none found.
    """
    if not isinstance(text, str):
        return []
    # capture ```json ... ``` and ``` ... ```
    blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)```", text, flags=re.IGNORECASE)
    return [b.strip() for b in blocks if b and b.strip()]


def find_brace_substring(text: str) -> Optional[str]:
    """
    Naive search for the largest substring that starts with { or [ and ends with matching } or ].
    This tries to find a JSON-like substring.
    """
    if not isinstance(text, str):
        return None
    # Find first occurrence of { or [
    start_idx = None
    for i, ch in enumerate(text):
        if ch in ('{', '['):
            start_idx = i
            break
    if start_idx is None:
        return None

    # Try to find a matching closing brace by scanning forward counting nesting.
    stack = []
    pairs = {'{': '}', '[': ']'}
    for j in range(start_idx, len(text)):
        ch = text[j]
        if ch in ('{', '['):
            stack.append(ch)
        elif ch in ('}', ']') and stack:
            # if matches, pop
            top = stack[-1]
            if (top == '{' and ch == '}') or (top == '[' and ch == ']'):
                stack.pop()
                if not stack:
                    # candidate substring
                    return text[start_idx:j+1]
            else:
                # mismatched - continue
                continue
    return None


def parse_maybe_json(text: str) -> Union[dict, list, str]:
    """
    Attempt multiple strategies to parse JSON from an LLM text response.

    Returns:
      - dict or list if valid JSON found and parsed,
      - otherwise original text (string).
    """
    if not isinstance(text, str):
        return text

    text = text.strip()
    if not text:
        return text

    # 1) direct parse
    parsed = safe_json_loads(text)
    if parsed is not None:
        return parsed

    # 2) extract from triple-backtick blocks
    blocks = extract_code_blocks(text)
    for b in blocks:
        p = safe_json_loads(b)
        if p is not None:
            return p

    # 3) try to find brace-delimited substring
    cand = find_brace_substring(text)
    if cand:
        p = safe_json_loads(cand)
        if p is not None:
            return p

    # 4) give up -> return original text
    return text
