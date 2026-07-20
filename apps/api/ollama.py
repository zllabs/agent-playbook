import json
import os
from typing import Optional

import httpx

from models import SkillWithReason

OLLAMA_BASE_URL = os.environ.get("OLLAMA_BASE_URL", "")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3")


def maybe_polish(task: str, skills: list[SkillWithReason]) -> list[SkillWithReason]:
    if not OLLAMA_BASE_URL:
        return skills
    try:
        return _polish_with_ollama(task, skills)
    except Exception:
        return skills


def _polish_with_ollama(task: str, skills: list[SkillWithReason]) -> list[SkillWithReason]:
    skill_list = "\n".join(f"- {s.id}: {s.title} (current reason: {s.reason})" for s in skills)
    prompt = f"""Task: {task}

Skills to explain (one short reason each, same order):
{skill_list}

Return JSON array of strings, one reason per skill. Example: ["reason1", "reason2"]"""

    with httpx.Client(timeout=30.0) as client:
        resp = client.post(
            f"{OLLAMA_BASE_URL.rstrip('/')}/api/generate",
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        )
        resp.raise_for_status()
        text = resp.json().get("response", "")

    reasons = _parse_reasons(text, len(skills))
    if not reasons:
        return skills

    return [
        SkillWithReason(**{**s.model_dump(), "reason": reasons[i]})
        for i, s in enumerate(skills)
    ]


def _parse_reasons(text: str, expected: int) -> Optional[list[str]]:
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        return None
    try:
        reasons = json.loads(text[start : end + 1])
        if isinstance(reasons, list) and len(reasons) == expected:
            return [str(r) for r in reasons]
    except json.JSONDecodeError:
        pass
    return None
