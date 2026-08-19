"""Intent matching checks for recommend search."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from search_match import score_skill, tokenize

PONYTAIL = {
    "id": "ponytail",
    "title": "Ponytail",
    "description": (
        "Makes your AI agent think like the laziest senior dev in the room. "
        "YAGNI, reuse-first, minimal diff — the best code is the code you never wrote."
    ),
    "tags": ["yagni", "minimal", "lazy", "architecture", "refactoring", "simplicity", "cursor", "rules"],
    "search_hints": [
        "lazy senior developer",
        "laziest senior dev",
        "best code is the code you never wrote",
        "minimal diff smallest change",
        "yagni reuse existing code",
        "avoid over engineering",
        "simplest solution that works",
        "write less code",
    ],
}

REFINER = {
    "id": "prompt-refiner",
    "title": "Prompt Refiner",
    "description": "Turn vague coding requests into concise structured briefs for coding agents.",
    "tags": ["prompts", "planning", "cursor", "workflow", "refine", "brief"],
    "search_hints": [
        "vague coding request",
        "underspecified task",
        "refine prompt before coding",
        "structure developer intent",
    ],
}

task = (
    "Makes your AI agent think like the laziest senior dev in the room. "
    "The best code is the code you never wrote."
)
score, tags, intents = score_skill(task, PONYTAIL)
assert score > 0, (score, tags, intents)
assert intents, f"expected intent match, got score={score} tags={tags}"
print(f"OK: ponytail intent score={score:.1f} intents={intents[:2]}")

refine_score, _, _ = score_skill("refine vague prompts before coding", REFINER)
assert refine_score > 0
print("OK: prompt-refiner intent")

generic_score, _, _ = score_skill("Describe a task. Get a Cursor skill Playbook.", REFINER)
assert generic_score == 0.0
print("OK: generic cursor task skips refiner")

assert "senior" in tokenize("laziest senior dev")
print("OK: tokenize")
