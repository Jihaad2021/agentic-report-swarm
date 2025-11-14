# src/agentic_report_swarm/agents/generic_agent.py
from typing import Dict, Any, Optional
from ..core.base_agent import BaseAgent
from ..utils import prompt_loader
from ..utils import llm_json

class GenericAgent(BaseAgent):
    """
    Template-driven LLM-backed agent which will attempt to parse JSON responses.
    """

    def __init__(self, name: str, llm_client=None, template: Optional[Dict[str, Any]] = None, config: Dict[str, Any] = None):
        super().__init__(name, config=config)
        self.llm = llm_client
        self.template = template

    def _get_template_dict(self, task: Dict[str, Any]) -> Dict[str, Any]:
        if isinstance(self.template, dict):
            return self.template
        if isinstance(self.template, str):
            try:
                return prompt_loader.load_yaml_template(self.template)
            except Exception:
                return {"prompt": self.template}
        return {"prompt": "Perform {{ task.type }} on topic {{ task.payload.topic }} (task id {{ task.id }})"}

    def _render_prompt(self, task: Dict[str, Any]) -> str:
        tpl = self._get_template_dict(task)
        context = {"task": task}
        return prompt_loader.render_template(tpl, context)

    def run(self, task: Dict[str, Any]) -> Dict[str, Any]:
        prompt = self._render_prompt(task)
        if not self.llm:
            raise RuntimeError("No llm client provided to GenericAgent")
        text = self.llm.generate(prompt)

        # Try to parse JSON (returns dict/list) else returns original text
        parsed = llm_json.parse_maybe_json(text)

        result: Dict[str, Any] = {"text": text, "meta": {"agent": self.name, "task_id": task.get("id")}}
        # If parsed is structured, include as `json` key for consumers
        if isinstance(parsed, (dict, list)):
            result["json"] = parsed
        return result
