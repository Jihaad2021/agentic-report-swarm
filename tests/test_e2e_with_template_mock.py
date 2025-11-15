# tests/test_e2e_with_template_mock.py
import json
import re
from agentic_report_swarm.utils.llm_json import parse_maybe_json
from agentic_report_swarm.utils.llm_client import LLMClient
from agentic_report_swarm.orchestrator.super_agent import run_topic
from agentic_report_swarm.utils.template_registry import TemplateRegistry

class TemplateEchoMockAdapter:
    """
    Robust mock adapter that:
    - tries parse_maybe_json(prompt) first,
    - if not, finds ALL brace-delimited substrings and tries to parse each (preferring ones with quotes/arrays),
    - also tries code blocks as fallback,
    - otherwise returns a fallback informative string.
    """
    def _find_brace_candidates(self, text: str):
        """Yield candidate substrings starting at every '{' with balanced braces."""
        starts = [m.start() for m in re.finditer(r'\{', text)]
        n = len(text)
        for start in starts:
            stack = []
            for j in range(start, n):
                ch = text[j]
                if ch == '{':
                    stack.append('{')
                elif ch == '}' and stack:
                    stack.pop()
                    if not stack:
                        yield text[start:j+1]
                        break

    def generate(self, prompt: str, **kwargs) -> str:
        # 1) try the general parser (handles direct JSON / codeblocks / embedded JSON heuristics)
        parsed = parse_maybe_json(prompt)
        if isinstance(parsed, (dict, list)):
            return json.dumps(parsed, ensure_ascii=False)

        # 2) try brace-candidates (prefer ones that look like real JSON)
        candidates = list(self._find_brace_candidates(prompt))
        # sort candidates by heuristic score: presence of double quotes or square brackets -> likely JSON
        def score(c):
            s = 0
            if '"' in c:
                s += 2
            if "'" in c:
                s += 0  # single quotes less likely valid JSON
            if '[' in c or ']' in c:
                s += 1
            s += min(1, len(c) / 1000)
            return -s  # negative for reverse sort = highest score first
        candidates.sort(key=score)

        for cand in candidates:
            try:
                p = parse_maybe_json(cand)
                if isinstance(p, (dict, list)):
                    return json.dumps(p, ensure_ascii=False)
            except Exception:
                # try direct json.loads with simple cleanups
                try:
                    maybe = cand.replace("'", '"')
                    maybe = re.sub(r',\s*([\]\}])', r'\1', maybe)
                    p2 = json.loads(maybe)
                    return json.dumps(p2, ensure_ascii=False)
                except Exception:
                    continue

        # 3) fallback: check triple-backtick blocks
        blocks = re.findall(r"```(?:json)?\s*([\s\S]*?)```", prompt, flags=re.IGNORECASE)
        for b in blocks:
            try:
                p = parse_maybe_json(b)
                if isinstance(p, (dict, list)):
                    return json.dumps(p, ensure_ascii=False)
            except Exception:
                continue

        # 4) last resort fallback message
        return f"[TEMPLATE-ECHO-MOCK] No JSON example found in prompt. Prompt snippet: {prompt[:200]}"


def test_end_to_end_with_template_echo_mock():
    # ensure templates are loaded from config/agent_templates
    registry = TemplateRegistry()
    templates = registry.templates
    assert templates, "No templates found under config/agent_templates — ensure YAML files exist."

    # create robust mock LLM client
    adapter = TemplateEchoMockAdapter()
    client = LLMClient(adapter)

    # run pipeline with explicit templates so factory doesn't rely on cwd
    md = run_topic("quantum computing", templates=templates, llm_client=client)

    # assertions
    assert "Research Report" in md
    assert "Key facts" in md or "Key facts:" in md
    assert "Top trends" in md or "Top trends:" in md
    assert "####" in md
    assert "validated" in md.lower() or "Source:" in md
    assert len(md) > 200
