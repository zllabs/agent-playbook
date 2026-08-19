from __future__ import annotations

import re
from datetime import datetime, timezone

from db import get_edges_for_skills, search_skills
from models import Playbook, PlaybookEdge, SkillWithReason


def recommend(task: str, polish_fn=None) -> Playbook:
    results = search_skills(task)
    selected = _select_skills(results)

    if not selected:
        return Playbook(
            title="No matches",
            task=task,
            skills=[],
            edges=[],
            generated_at=_now(),
        )

    selected, raw_edges = _coalesce_playbook(selected)

    skills: list[SkillWithReason] = []
    for skill, score, matched_tags, matched_intents in selected:
        reason = _template_reason(
            skill, matched_tags, score, matched_intents=matched_intents, related=score < 1.0 and not matched_tags
        )
        skills.append(SkillWithReason(**{k: v for k, v in skill.items() if k != "search_hints"}, reason=reason))

    if polish_fn and skills:
        skills = polish_fn(task, skills)

    edges = [
        PlaybookEdge(from_=e["from_id"], to=e["to_id"], type=e["type"])
        for e in raw_edges
    ]

    title = _playbook_title(task, skills)

    return Playbook(
        title=title,
        task=task,
        skills=skills,
        edges=edges,
        generated_at=_now(),
    )


def _select_skills(results: list[tuple[dict, float, list[str], list[str]]]) -> list[tuple[dict, float, list[str], list[str]]]:
    """Top scored skills plus connected neighbors that also matched the task."""
    if not results:
        return []

    by_id = {skill["id"]: (skill, score, tags, intents) for skill, score, tags, intents in results}
    top = results[:8]
    chosen_ids = {s["id"] for s, _, _, _ in top}

    for edge in get_edges_for_skills(chosen_ids):
        for sid in (edge["from_id"], edge["to_id"]):
            if sid not in chosen_ids and sid in by_id:
                _, nscore, ntags, nintents = by_id[sid]
                if ntags or nintents:
                    top.append(by_id[sid])
                    chosen_ids.add(sid)
            if len(top) >= 8:
                break
        if len(top) >= 8:
            break

    return top[:8]


def _coalesce_playbook(
    selected: list[tuple[dict, float, list[str], list[str]]],
) -> tuple[list[tuple[dict, float, list[str], list[str]]], list[dict]]:
    """Drop isolated orphans when a connected cluster exists."""
    skill_ids = {s["id"] for s, _, _, _ in selected}
    edges = get_edges_for_skills(skill_ids)

    connected_ids: set[str] = set()
    for e in edges:
        if e["from_id"] in skill_ids and e["to_id"] in skill_ids:
            connected_ids.add(e["from_id"])
            connected_ids.add(e["to_id"])

    if len(connected_ids) >= 2:
        # Never drop the top-ranked skill even if it has no edges in this set
        # (weak tag collisions can form a cluster that would otherwise orphan it).
        keep = connected_ids | {selected[0][0]["id"]}
        selected = [item for item in selected if item[0]["id"] in keep]
        skill_ids = {s["id"] for s, _, _, _ in selected}
        edges = [e for e in edges if e["from_id"] in skill_ids and e["to_id"] in skill_ids]

    return selected, edges


def _template_reason(
    skill: dict,
    matched_tags: list[str],
    score: float,
    *,
    matched_intents: list[str] | None = None,
    related: bool = False,
) -> str:
    if related:
        return "Related skill — connected in the catalog graph."
    if matched_intents:
        return f"Matched intent: {matched_intents[0]}."
    if matched_tags:
        tags = ", ".join(sorted(set(matched_tags)))
        return f"Matched tags: {tags}."
    return f"Relevant to your task — matched on {skill['title']}."


def _playbook_title(task: str, skills: list[SkillWithReason]) -> str:
    if not skills:
        return "Empty Playbook"
    # Use top skill tags + first few words of task
    words = re.findall(r"[A-Za-z0-9]+", task)[:4]
    prefix = " ".join(words).title() if words else skills[0].title
    return f"{prefix} Playbook"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
