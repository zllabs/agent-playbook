import json
from pathlib import Path

SOURCES_PATH = Path(__file__).resolve().parents[2] / "data" / "sources.json"
_sources = json.loads(SOURCES_PATH.read_text())

MDC_REPO = _sources["mdc_repo"]
MDC_RULES = f"{MDC_REPO}/tree/main/{_sources['mdc_rules_path']}"
PLAYBOOK_REPO = _sources["playbook_repo"]


def mdc_rule(name: str) -> str:
    return f"{MDC_REPO}/blob/main/{_sources['mdc_rules_path']}/{name}.mdc"


def playbook_skill_path(skill_id: str) -> str:
    return f"{PLAYBOOK_REPO}/tree/main/skills/{skill_id}"
