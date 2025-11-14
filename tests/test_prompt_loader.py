# tests/test_prompt_loader.py
from pathlib import Path
from agentic_report_swarm.utils.prompt_loader import render_template, load_yaml_template

def test_render_from_dict():
    tpl = {"prompt": "Hello {{ name }} - topic {{ task.payload.topic }}"}
    out = render_template(tpl, {"name": "tester", "task": {"payload": {"topic": "AI"}}})
    assert "Hello tester" in out
    assert "AI" in out

def test_load_yaml_and_render(tmp_path):
    p = tmp_path / "test_template.yaml"
    p.write_text("prompt: |\n  Topic: {{ task.payload.topic }}\n  ID: {{ task.id }}\n")
    loaded = load_yaml_template(p)
    out = render_template(loaded, {"task": {"payload": {"topic": "ml"}, "id": "t123"}})
    assert "Topic: ml" in out
    assert "ID: t123" in out
