# src/app.py
"""
Simple CLI to run SuperAgent in mock mode.

Usage:
    python -m src.app --topic "e-commerce fashion Indonesia Q4" --length short --mock
"""

import argparse
import os
from agentic_report_swarm.orchestrator.super_agent import SuperAgent
from agentic_report_swarm.adapters.openai_adapter import MockOpenAIAdapter, OpenAIAdapter

def build_adapters(mock: bool):
    if mock:
        return {"openai": MockOpenAIAdapter(canned={})}
    # real adapter (not used by default)
    return {"openai": OpenAIAdapter()}

def main():
    parser = argparse.ArgumentParser(description="Run Agentic Report Swarm (MVP) - mock mode")
    parser.add_argument("--topic", required=True, help="Topic for the report")
    parser.add_argument("--length", default="short", choices=["short", "detailed"], help="Length of report")
    parser.add_argument("--mock", action="store_true", help="Use mock adapters (no OpenAI calls)")
    args = parser.parse_args()

    adapters = build_adapters(mock=args.mock)
    sa = SuperAgent(adapters=adapters, max_workers=3)
    command = {"topic": args.topic, "length": args.length}
    print(f"Starting SuperAgent for topic: {args.topic} (mock={args.mock})")
    out = sa.run(command, save=True)
    print(f"Report saved to: {out['report_path']}")
    print("--- Report preview ---")
    print(out['markdown'][:1000])  # print first 1000 chars

if __name__ == "__main__":
    main()
