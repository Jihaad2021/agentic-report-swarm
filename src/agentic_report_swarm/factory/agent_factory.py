# src/agentic_report_swarm/factory/agent_factory.py
from typing import Dict, Any, Optional
from ..agents.generic_agent import GenericAgent
from ..utils.llm_client import LLMClient
from ..utils.template_registry import TemplateRegistry

class AgentFactory:
    """
    Build agents and inject templates automatically.

    Behavior:
    - If `templates` dict passed explicitly, use it.
    - Else auto-load templates from config/agent_templates (via TemplateRegistry).
    """
    def __init__(self, llm_client: Optional[LLMClient] = None, templates: Optional[Dict[str, Dict]] = None, template_dir: Optional[str] = None):
        self.llm_client = llm_client or LLMClient.from_env(prefer_real=False)
        if templates is not None:
            self.templates = templates
        else:
            registry = TemplateRegistry(template_dir)
            self.templates = registry.templates

    def build(self, agent_type: str):
        """
        Build GenericAgent with template if available.
        agent_type -> template key expected to match filename in config/agent_templates/
        """
        tpl = self.templates.get(agent_type)
        name = f"{agent_type}_agent"
        # If tpl is a dict, pass it directly. If tpl is a path (string), GenericAgent can handle path strings.
        return GenericAgent(name=name, llm_client=self.llm_client, template=tpl)
