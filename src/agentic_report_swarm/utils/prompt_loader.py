# src/agentic_report_swarm/utils/prompt_loader.py
"""
Prompt loader & renderer using jinja2.

Functions:
- load_yaml_template(path: Path) -> dict
- render_template(template: Union[dict, str], context: dict) -> str

Template can be:
- a dict {'prompt': '...'} (loaded from YAML)
- a raw string prompt
"""
from pathlib import Path
from typing import Union, Dict, Any
import yaml

try:
    from jinja2 import Template, StrictUndefined
except Exception as e:
    raise RuntimeError("jinja2 is required for prompt rendering. Install with `pip install jinja2`.") from e


def load_yaml_template(path: Union[str, Path]) -> Dict[str, Any]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Template file not found: {path}")
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict):
        raise ValueError("Template YAML must contain a mapping at top-level (e.g. {'prompt': '...'}).")
    return data


def render_template(template: Union[Dict[str, Any], str], context: Dict[str, Any]) -> str:
    """
    Render a template (dict with 'prompt' key OR raw string) using jinja2.
    Context is a mapping that will contain at least 'task' key.
    """
    if isinstance(template, dict):
        tpl_str = template.get("prompt") or template.get("template") or ""
    else:
        tpl_str = template

    if tpl_str is None:
        tpl_str = ""

    # Create Jinja2 template with strict undefined to surface missing keys quickly.
    jtpl = Template(tpl_str, undefined=StrictUndefined)
    # Best practice: provide the whole context object as 'task' and allow top-level destructuring via dot/dict access.
    render_ctx = dict(context)
    return jtpl.render(**render_ctx)
