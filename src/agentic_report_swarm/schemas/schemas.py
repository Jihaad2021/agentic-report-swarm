# src/agentic_report_swarm/schemas/schemas.py
from typing import List, Optional
try:
    # pydantic v1/v2 compatibility
    from pydantic import BaseModel, ValidationError
except Exception as e:
    raise RuntimeError("pydantic is required for schema validation. Install with `pip install pydantic`.") from e

# Example schema for research agent
class ResearchResult(BaseModel):
    title: str
    key_facts: List[str]
    sources: List[str]
    summary: Optional[str] = None

# Example schema for trends agent
class TrendsResult(BaseModel):
    trend_summary: str
    top_trends: List[str]
    timeframe: Optional[str] = None

# Example schema for insights agent
class InsightsResult(BaseModel):
    insights: List[str]
    implications: Optional[List[str]] = None
    confidence: Optional[float] = None

# Example schema for writer agent (final sections)
class WriterResult(BaseModel):
    sections: List[dict]  # each section: {"heading": str, "content": str}
    metadata: Optional[dict] = None

# Map agent type -> schema class
MODEL_MAP = {
    "research": ResearchResult,
    "trends": TrendsResult,
    "insights": InsightsResult,
    "writer": WriterResult,
}

# expose ValidationError for callers
__all__ = ["MODEL_MAP", "ValidationError"]
