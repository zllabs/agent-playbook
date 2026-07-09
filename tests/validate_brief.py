"""Agent Brief structure compliance and brief quality checks."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Literal

REQUIRED_SECTIONS = ("Task:", "Context:", "Requirements:", "Verification:")
FORBIDDEN_PHRASES = (
    "you are an expert",
    "you are a senior",
    "think step by step",
    "follow best practices",
    "carefully analyze",
)
WORD_TARGET_MIN = 20
WORD_TARGET_MAX = 50
WORD_HARD_LIMIT = 200
WORD_TARGET_LABEL = "20–50"
FILE_PATH_PATTERN = re.compile(r"[\w./-]+\.(?:ts|tsx|py|js|go|rb|java)")


@dataclass
class BriefExample:
    number: int
    title: str
    request: str
    body: str
    kind: Literal["brief", "clarification"]
    category: str = ""


def word_count(text: str) -> int:
    return len(text.split())


def check_structure_compliance(body: str) -> list[str]:
    errors: list[str] = []
    for section in REQUIRED_SECTIONS:
        if section not in body:
            errors.append(f"missing section: {section}")
    return errors


def check_no_role_play_fluff(body: str) -> list[str]:
    errors: list[str] = []
    lowered = body.lower()
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            errors.append(f"role-play fluff: {phrase}")
    return errors


def check_word_limit(body: str) -> list[str]:
    count = word_count(body)
    if count > WORD_HARD_LIMIT:
        return [f"word count {count} exceeds hard limit {WORD_HARD_LIMIT}"]
    return []


def check_no_invented_context(request: str, body: str) -> list[str]:
    """Flag project-specific paths in the brief that were not in the request.

    Generic inference (e.g. "database migration" for "run the migration") is
    allowed. Named files, modules, and services are not.
    """
    errors: list[str] = []
    request_lower = request.lower()
    for match in FILE_PATH_PATTERN.finditer(body):
        path = match.group(0)
        if path.lower() not in request_lower:
            errors.append(f"invented context: {path}")
    return errors


def check_brief_quality(request: str, body: str) -> list[str]:
    """Run all brief quality checks."""
    errors: list[str] = []
    errors.extend(check_structure_compliance(body))
    errors.extend(check_no_role_play_fluff(body))
    errors.extend(check_word_limit(body))
    errors.extend(check_no_invented_context(request, body))
    return errors


def parse_examples_markdown(content: str) -> list[BriefExample]:
    examples: list[BriefExample] = []
    current_category = ""
    for line in content.splitlines():
        category_match = re.match(r"^## ([^#].+)$", line)
        if category_match and not line.startswith("## Skipped"):
            current_category = category_match.group(1).strip()
            continue
        example_match = re.match(r"^### (\d+)\.\s+(.+)$", line)
        if not example_match:
            continue
        number = int(example_match.group(1))
        title = example_match.group(2).strip()
        start = content.index(line)
        next_heading = re.search(r"\n### \d+\.|\n## ", content[start + 1:])
        end = start + 1 + next_heading.start() if next_heading else len(content)
        section = content[start:end]
        request_match = re.search(r"\*\*Request:\*\*\s+`([^`]+)`", section)
        if not request_match:
            continue
        request = request_match.group(1)
        if "**Response:**" in section:
            response_match = re.search(r"\*\*Response:\*\*\s+(.+)", section)
            body = response_match.group(1).strip() if response_match else ""
            examples.append(
                BriefExample(
                    number, title, request, body,
                    kind="clarification", category=current_category,
                )
            )
            continue
        code_blocks = re.findall(r"```(?:[^\n]*\n)?(.*?)```", section, re.DOTALL)
        if not code_blocks:
            continue
        body = code_blocks[0].strip()
        examples.append(
            BriefExample(
                number, title, request, body,
                kind="brief", category=current_category,
            )
        )
    return examples


def parse_skipped_requests(content: str) -> list[str]:
    skipped_section = re.search(
        r"## Skipped — already specific\n\n.*?\n\n\| Request \|",
        content,
        re.DOTALL,
    )
    if not skipped_section:
        return []
    table = content[skipped_section.start() :]
    rows = re.findall(r"\| `([^`]+)` \|", table)
    return rows
