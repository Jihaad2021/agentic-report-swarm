# tests/test_llm_json.py
from agentic_report_swarm.utils.llm_json import parse_maybe_json

def test_parse_plain_json():
    txt = '{"a": 1, "b": [1,2,3]}'
    out = parse_maybe_json(txt)
    assert isinstance(out, dict)
    assert out['a'] == 1

def test_parse_json_in_backticks():
    txt = "Here is the result:\n```json\n{\"x\": 10, \"y\": \"ok\"}\n```"
    out = parse_maybe_json(txt)
    assert isinstance(out, dict)
    assert out['x'] == 10

def test_parse_json_embedded_in_text():
    txt = "Explanation... {\"k\": \"v\", \"n\": 5} ...end"
    out = parse_maybe_json(txt)
    assert isinstance(out, dict)
    assert out['k'] == 'v'

def test_non_json_returns_text():
    txt = "This is plain English, nothing to parse."
    out = parse_maybe_json(txt)
    assert isinstance(out, str)
    assert out == txt
