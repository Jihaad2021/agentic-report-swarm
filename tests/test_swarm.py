# tests/test_swarm.py
from agentic_report_swarm.orchestrator.super_agent import run_topic
from agentic_report_swarm.utils.llm_client import LLMClient
from agentic_report_swarm.adapters.openai_adapter import MockOpenAIAdapter

def test_end_to_end_pipeline_generates_markdown():
    # create mock llm client and default templates (simple prompt strings)
    adapter = MockOpenAIAdapter()
    client = LLMClient(adapter)
    # simple templates to prove prompt rendering path exists (optional)
    templates = {
        "research": {"prompt": "Research about {task[payload][topic]}"},
        "trends": {"prompt": "Find trends about {task[payload][topic]}"},
        "insights": {"prompt": "Generate insights for {task[payload][topic]}"},
        "writer": {"prompt": "Write a report for {task[payload][topic]}"},
    }
    md = run_topic("quantum computing", templates=templates, llm_client=client)
    assert "Research Report" in md
    # should contain sections for each task type
    assert "### research" in md.lower() or "### research" in md
    assert "### writer" in md.lower() or "### writer" in md
    # writer output should appear (mock adapter returns a string)
    assert "Generated for" in md or "[MOCK-ADAPTER]" in md
