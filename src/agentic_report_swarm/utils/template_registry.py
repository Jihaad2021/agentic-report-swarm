# src/agentic_report_swarm/utils/template_registry.py
"""
Template registry / discovery.

Responsibilities:
- discover YAML/JSON template files under a directory (default: config/agent_templates/)
- load them into a dict mapping key -> template dict
- provide helper to get single template by name
- validate basic shape (must be a mapping and contain 'prompt' key ideally)
"""

from pathlib import Path
from typing import Dict, Any, Optional
import yaml

DEFAULT_TEMPLATE_DIR = Path("config/agent_templates")

class TemplateRegistry:
    def __init__(self, template_dir: Optional[Path] = None):
        self.template_dir = Path(template_dir) if template_dir else DEFAULT_TEMPLATE_DIR
        self.templates: Dict[str, Dict[str, Any]] = {}
        self.load_all()

    def load_all(self) -> Dict[str, Dict[str, Any]]:
        """Discover and load all .yaml/.yml/.json files in template_dir."""
        self.templates = {}
        if not self.template_dir.exists():
            return self.templates
        for p in sorted(self.template_dir.glob("*")):
            if p.suffix.lower() not in (".yaml", ".yml", ".json"):
                continue
            try:
                raw = yaml.safe_load(p.read_text())
                if isinstance(raw, dict):
                    # key name: filename without extension
                    key = p.stem
                    self.templates[key] = raw
                else:
                    # skip non-mapping files
                    continue
            except Exception:
                # skip broken files (could log)
                continue
        return self.templates

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        return self.templates.get(name)

    def refresh(self) -> Dict[str, Dict[str, Any]]:
        """Reload from disk."""
        return self.load_all()
