# tests/test_aggregator_structured.py
from agentic_report_swarm.orchestrator.aggregator import aggregate_to_markdown
from agentic_report_swarm.core.plan_schema import Plan, SubTask
import json

def _make_plan():
    plan = Plan(plan_id="p1", topic="test-topic", subtasks=[
        SubTask(id="t1", type="research", payload={}),
        SubTask(id="t2", type="trends", payload={}, depends_on=["t1"]),
        SubTask(id="t3", type="insights", payload={}, depends_on=["t2"]),
        SubTask(id="t4", type="writer", payload={}, depends_on=["t3"]),
    ])
    return plan

def test_aggregator_prefers_validated():
    plan = _make_plan()
    # mock results: t1 validated research
    r = {}
    r["t1"] = {"id":"t1","success":True,"output":{"text":"raw text","meta":{"agent":"a1"},"json":{"title":"T","key_facts":["k1"],"sources":["s1"]},"validated":True,"validated_data":{"title":"T","key_facts":["k1"],"sources":["s1"]}}}
    # t2 unvalidated json
    r["t2"] = {"id":"t2","success":True,"output":{"text":"raw t2","meta":{"agent":"a2"},"json":{"trend_summary":"S","top_trends":["a","b"]}}}
    # t3 only text
    r["t3"] = {"id":"t3","success":True,"output":{"text":"insights text","meta":{"agent":"a3"}}}
    # t4 writer validated sections
    r["t4"] = {"id":"t4","success":True,"output":{"text":"writer raw","meta":{"agent":"a4"},"json":{"sections":[{"heading":"Intro","content":"This is intro"}]},"validated":True,"validated_data":{"sections":[{"heading":"Intro","content":"This is intro"}]}}}

    md = aggregate_to_markdown(plan, r)
    # check important bits
    assert "Research Report" in md
    assert "Key facts" in md or "Key facts" in md
    assert "Top trends" in md
    assert "insights text" in md
    assert "#### Intro" in md
    # provenance
    assert "Source: a1" in md
    assert "unvalidated JSON" in md  # t2 should be labeled unvalidated
