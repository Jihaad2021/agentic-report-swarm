# tests/test_template_registry.py
from pathlib import Path
import tempfile
import shutil
from agentic_report_swarm.utils.template_registry import TemplateRegistry
from agentic_report_swarm.factory.agent_factory import AgentFactory
from agentic_report_swarm.utils.llm_client import LLMClient
from agentic_report_swarm.adapters.openai_adapter import MockOpenAIAdapter

def test_template_registry_and_factory(tmp_path):
    # create a fake config dir
    cfg_dir = tmp_path / "agent_templates"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    # write a sample template file research.yaml
    (cfg_dir / "research.yaml").write_text(
        "prompt: |\n  Research about {{ task.payload.topic }}\n"
    )
    # instantiate registry pointing to tmp dir
    reg = TemplateRegistry(template_dir=cfg_dir)
    assert "research" in reg.templates
    tpl = reg.get("research")
    assert isinstance(tpl, dict)
    # test AgentFactory auto-load from this directory
    client = LLMClient(MockOpenAIAdapter())
    af = AgentFactory(llm_client=client, templates=None, template_dir=cfg_dir)
    agent = af.build("research")
    # agent should have template dict (or at least not None)
    assert agent.template is not None
    # run agent quickly (mock LLM returns predictable string)
    res = agent.run({"id": "t1", "type": "research", "payload": {"topic": "X"}})
    assert "Generated for" in res["text"] or "[MOCK-ADAPTER]" in res["text"]
