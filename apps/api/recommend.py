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
    for skill, score, matched_tags in selected:
        reason = _template_reason(skill, matched_tags, score, related=score < 1.0 and not matched_tags)
        skills.append(SkillWithReason(**skill, reason=reason))

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


def _select_skills(results: list[tuple[dict, float, list[str]]]) -> list[tuple[dict, float, list[str]]]:
    """Top scored skills plus connected neighbors that also matched the task."""
    if not results:
        return []

    by_id = {skill["id"]: (skill, score, tags) for skill, score, tags in results}
    top = results[:8]
    chosen_ids = {s["id"] for s, _, _ in top}

    for edge in get_edges_for_skills(chosen_ids):
        for sid in (edge["from_id"], edge["to_id"]):
            if sid not in chosen_ids and sid in by_id:
                _, _, ntags = by_id[sid]
                if ntags:
                    top.append(by_id[sid])
                    chosen_ids.add(sid)
            if len(top) >= 8:
                break
        if len(top) >= 8:
            break

    return top[:8]


def _coalesce_playbook(
    selected: list[tuple[dict, float, list[str]]],
) -> tuple[list[tuple[dict, float, list[str]]], list[dict]]:
    """Drop isolated orphans when a connected cluster exists."""
    skill_ids = {s["id"] for s, _, _ in selected}
    edges = get_edges_for_skills(skill_ids)

    connected_ids: set[str] = set()
    for e in edges:
        if e["from_id"] in skill_ids and e["to_id"] in skill_ids:
            connected_ids.add(e["from_id"])
            connected_ids.add(e["to_id"])

    if len(connected_ids) >= 2:
        selected = [item for item in selected if item[0]["id"] in connected_ids]
        skill_ids = {s["id"] for s, _, _ in selected}
        edges = [e for e in edges if e["from_id"] in skill_ids and e["to_id"] in skill_ids]

    return selected, edges


def _template_reason(
    skill: dict, matched_tags: list[str], score: float, related: bool = False
) -> str:
    if related:
        return "Related skill — connected in the catalog graph."
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
