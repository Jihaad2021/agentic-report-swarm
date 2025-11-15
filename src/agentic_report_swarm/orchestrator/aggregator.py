# src/agentic_report_swarm/orchestrator/aggregator.py
from typing import Dict, Any
import json
from ..core.plan_schema import Plan

def _pretty_json(obj: Any) -> str:
    try:
        return json.dumps(obj, indent=2, ensure_ascii=False)
    except Exception:
        return str(obj)

def _render_research(validated: Dict[str, Any]) -> str:
    parts = []
    title = validated.get("title")
    if title:
        parts.append(f"**Title:** {title}\n")
    key_facts = validated.get("key_facts") or []
    if key_facts:
        parts.append("**Key facts:**\n")
        for k in key_facts:
            parts.append(f"- {k}")
        parts.append("")  # newline
    sources = validated.get("sources") or []
    if sources:
        parts.append("**Sources:**")
        for s in sources:
            parts.append(f"- {s}")
    summary = validated.get("summary")
    if summary:
        parts.append("\n**Summary:**\n")
        parts.append(summary)
    return "\n".join(parts)

def _render_trends(validated: Dict[str, Any]) -> str:
    parts = []
    timeframe = validated.get("timeframe")
    if timeframe:
        parts.append(f"**Timeframe:** {timeframe}\n")
    parts.append(f"**Trend summary:**\n{validated.get('trend_summary','')}\n")
    top = validated.get("top_trends") or []
    if top:
        parts.append("**Top trends:**")
        for t in top:
            parts.append(f"- {t}")
    return "\n".join(parts)

def _render_insights(validated: Dict[str, Any]) -> str:
    parts = []
    insights = validated.get("insights") or []
    if insights:
        parts.append("**Insights:**")
        for i in insights:
            parts.append(f"- {i}")
    impl = validated.get("implications") or []
    if impl:
        parts.append("\n**Implications:**")
        for im in impl:
            parts.append(f"- {im}")
    conf = validated.get("confidence")
    if conf is not None:
        parts.append(f"\n**Confidence:** {conf}")
    return "\n".join(parts)

def _render_writer(validated: Dict[str, Any]) -> str:
    """
    WriterResult schema: sections: List[dict] with keys heading, content
    """
    parts = []
    sections = validated.get("sections") or []
    for sec in sections:
        heading = sec.get("heading") or sec.get("title") or "Section"
        content = sec.get("content") or sec.get("body") or ""
        parts.append(f"#### {heading}\n\n{content}\n")
    meta = validated.get("metadata")
    if meta:
        parts.append("**Metadata:**")
        parts.append(_pretty_json(meta))
    return "\n".join(parts)

# mapping task type -> renderer
_RENDERER = {
    "research": _render_research,
    "trends": _render_trends,
    "insights": _render_insights,
    "writer": _render_writer,
}

def aggregate_to_markdown(plan: Plan, results: Dict[str, Dict[str, Any]]) -> str:
    """
    Build deterministic markdown from plan + results. Prefer structured validated_data when present.
    """
    parts = [f"# Research Report — {plan.topic}\n"]
    for st in plan.subtasks:
        parts.append(f"---\n## {st.type.capitalize()} (task {st.id})\n")
        r = results.get(st.id)
        if not r:
            parts.append("_No result_\n")
            continue

        # provenance header
        agent_name = None
        if isinstance(r.get("output"), dict):
            agent_name = r["output"].get("meta", {}).get("agent")
        if not agent_name:
            agent_name = r.get("output", {}).get("meta", {}).get("agent") if isinstance(r.get("output"), dict) else None
        if not agent_name:
            agent_name = r.get("meta", {}).get("agent") if isinstance(r.get("meta"), dict) else None

        # if success false: show error
        if not r.get("success"):
            parts.append(f"**FAILED**: {r.get('error')}\n")
            continue

        out = r.get("output") or {}
        # If the agent already attached validated_data, prefer it
        validated = out.get("validated_data") if isinstance(out, dict) else None
        if validated:
            # call renderer if available
            renderer = _RENDERER.get(st.type)
            if renderer:
                try:
                    content = renderer(validated)
                except Exception:
                    content = _pretty_json(validated)
            else:
                content = _pretty_json(validated)
            # include provenance
            parts.append(f"_Source: {agent_name or 'unknown'} (validated)_\n\n")
            parts.append(content + "\n")
            continue

        # If no validated_data but json present (unvalidated),
        # try to render using renderer if available, otherwise show pretty JSON
        if isinstance(out, dict) and out.get("json") is not None:
            json_obj = out.get("json")
            renderer = _RENDERER.get(st.type)
            if renderer:
                try:
                    content = renderer(json_obj)
                except Exception:
                    content = _pretty_json(json_obj)
                parts.append(f"_Source: {agent_name or 'unknown'} (unvalidated JSON)_\n\n")
                parts.append(content + "\n")
            else:
                parts.append(f"_Source: {agent_name or 'unknown'} (unvalidated JSON)_\n\n")
                parts.append(_pretty_json(json_obj) + "\n")
            continue

        # Otherwise fallback to text field
        text = None
        if isinstance(out, dict):
            text = out.get("text")
        elif isinstance(out, str):
            text = out
        if text:
            parts.append(f"_Source: {agent_name or 'unknown'}_\n\n")
            parts.append(text + "\n")
            continue

        # If nothing, print raw r
        parts.append(_pretty_json(r) + "\n")

    # final newline
    return "\n".join(parts)
