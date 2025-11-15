# src/agentic_report_swarm/agents/generic_agent.py
from typing import Dict, Any, Optional
from ..core.base_agent import BaseAgent
from ..utils import prompt_loader
from ..utils import llm_json

# try import schemas MODEL_MAP if available
try:
    from ..schemas.schemas import MODEL_MAP, ValidationError as SchemaValidationError
except Exception:
    MODEL_MAP = {}
    SchemaValidationError = Exception

class GenericAgent(BaseAgent):
    """
    Template-driven LLM-backed agent which will attempt to parse JSON responses and validate against schema.
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
            # Attempt schema validation if schema for task.type exists
            schema_cls = MODEL_MAP.get(task.get("type"))
            if schema_cls:
                try:
                    # pydantic will coerce/validate types; store validated model
                    validated = schema_cls.parse_obj(parsed) if hasattr(schema_cls, "parse_obj") else schema_cls(**parsed)
                    result["validated"] = True
                    # attach model dict for downstream convenience
                    result["validated_data"] = validated.dict() if hasattr(validated, "dict") else dict(validated)
                except SchemaValidationError as e:
                    # don't raise — record validation errors for debugging and fallback
                    result["validated"] = False
                    # store the stringified error; keep raw text/json
                    result["validation_error"] = str(e)
        return result
