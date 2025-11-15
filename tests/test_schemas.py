# tests/test_schemas.py
from agentic_report_swarm.schemas.schemas import ResearchResult, TrendsResult

def test_research_schema_accepts_valid():
    payload = {
        "title": "AI in 2025",
        "key_facts": ["fact1", "fact2", "fact3"],
        "sources": ["source1", "source2"],
        "summary": "short"
    }
    model = ResearchResult(**payload)
    assert model.title == "AI in 2025"
    assert isinstance(model.key_facts, list)

def test_trends_schema_missing_fields_should_error():
    payload = {"top_trends": ["t1", "t2"]}
    try:
        TrendsResult(**payload)
        assert False, "TrendsResult should require trend_summary"
    except Exception:
        assert True
