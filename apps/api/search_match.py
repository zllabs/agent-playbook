"""Intent-aware skill matching for recommend/search."""

from __future__ import annotations

import re
from typing import Any

GENERIC_TAGS = frozenset({
    "cursor", "workflow", "planning", "skills", "rules", "documentation",
    "quality", "backend", "frontend", "api", "testing", "devops", "ui",
})

STOP_WORDS = frozenset({
    "a", "an", "the", "and", "or", "for", "to", "in", "on", "with", "using",
    "build", "make", "add", "create", "implement", "write", "set", "up", "my",
    "me", "i", "want", "need", "help", "like", "get", "how", "what", "when",
    "where", "which", "that", "this", "your", "you", "is", "are", "be", "do",
    "does", "can", "should", "would", "will", "into", "from", "about", "as",
    "at", "by", "it", "its", "of", "we", "our", "they", "them", "their",
    "agent", "ai", "room", "think", "makes",
})

STEM_SUFFIXES = ("iest", "iest", "ingly", "edly", "ing", "est", "er", "ed", "ly", "es", "s")


def tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in STOP_WORDS and len(w) > 1]


def stem(word: str) -> str:
    w = word.lower()
    for suffix in STEM_SUFFIXES:
        if len(w) > len(suffix) + 2 and w.endswith(suffix):
            return w[: -len(suffix)]
    return w


def _task_variants(task: str) -> tuple[set[str], set[str], str]:
    tokens = tokenize(task)
    literal = set(tokens)
    stems = {stem(t) for t in tokens}
    normalized = re.sub(r"\s+", " ", task.lower()).strip()
    return literal, stems, normalized


def _hint_matches(task_literals: set[str], task_stems: set[str], task_norm: str, hint: str) -> bool:
    hint_norm = re.sub(r"\s+", " ", hint.lower()).strip()
    if len(hint_norm) >= 10 and hint_norm in task_norm:
        return True
    hint_tokens = tokenize(hint)
    if len(hint_tokens) < 2:
        return hint_tokens[0] in task_literals if hint_tokens else False
    hits = 0
    for token in hint_tokens:
        if token in task_literals or stem(token) in task_stems:
            hits += 1
    return hits / len(hint_tokens) >= 0.6


def score_skill(
    task: str,
    skill: dict[str, Any],
    *,
    fts_rank: float | None = None,
) -> tuple[float, list[str], list[str]]:
    """Return (score, matched_tags, matched_intents)."""
    task_literals, task_stems, task_norm = _task_variants(task)
    if not task_literals and not task_norm:
        return 0.0, [], []

    tag_set = {t.lower() for t in skill["tags"]}
    title_lower = skill["title"].lower()
    desc_lower = skill["description"].lower()
    hints = [h for h in skill.get("search_hints", []) if h.strip()]

    score = 0.0
    matched_tags: list[str] = []
    matched_intents: list[str] = []

    for token in task_literals:
        stemmed = stem(token)
        if token in tag_set or stemmed in {stem(t) for t in tag_set}:
            if token in GENERIC_TAGS:
                score += 2.0
            else:
                score += 10.0
                matched_tags.append(token)
        elif token in title_lower or stemmed in title_lower:
            score += 6.0
        elif token in desc_lower or stemmed in desc_lower:
            score += 4.0

    for hint in hints:
        if _hint_matches(task_literals, task_stems, task_norm, hint):
            score += 22.0
            matched_intents.append(hint)

    title_hit = any(t in title_lower or stem(t) in title_lower for t in task_literals)
    desc_hits = sum(
        1
        for t in task_literals
        if t in desc_lower or stem(t) in desc_lower
    )

    has_signal = bool(matched_tags or matched_intents or title_hit or desc_hits >= 1)
    if not has_signal:
        return 0.0, [], []

    # Description-only matches need corroboration — avoid generic single-word leaks.
    if not (matched_tags or matched_intents or title_hit or desc_hits >= 2):
        return 0.0, [], []

    if fts_rank is not None:
        score += abs(fts_rank) * 4.0

    if score <= 0:
        return 0.0, [], []

    return score, matched_tags, matched_intents
