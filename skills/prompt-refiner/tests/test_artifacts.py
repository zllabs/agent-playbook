"""Tests for artifact consistency within the prompt-refiner package."""

from __future__ import annotations

import unittest
from pathlib import Path

from validate_brief import (
    WORD_TARGET_LABEL,
    check_no_invented_context,
    parse_examples_markdown,
)

PKG = Path(__file__).resolve().parents[1]
CURSOR_RULE = PKG / "cursor" / "rule.mdc"
CLAUDE_SKILL = PKG / "claude" / "SKILL.md"
EXAMPLES = PKG / "examples.md"


class TestArtifactSync(unittest.TestCase):
    def test_word_target_documented_consistently(self) -> None:
        label = f"{WORD_TARGET_LABEL} words"
        for path in (CURSOR_RULE, CLAUDE_SKILL, PKG / "README.md"):
            with self.subTest(path=path.name):
                self.assertIn(label, path.read_text())

    def test_debug_documented_in_cursor_and_skill(self) -> None:
        for path in (CURSOR_RULE, CLAUDE_SKILL):
            with self.subTest(path=path.name):
                self.assertIn("debug: true", path.read_text())

    def test_invented_context_wording_in_rules(self) -> None:
        phrase = "Never invent project-specific details"
        for path in (CURSOR_RULE, CLAUDE_SKILL):
            with self.subTest(path=path.name):
                self.assertIn(phrase, path.read_text())

    def test_examples_linked_from_artifacts(self) -> None:
        link = "github.com/zllabs/agent-brief/blob/main/skills/prompt-refiner/examples.md"
        for path in (CURSOR_RULE, CLAUDE_SKILL):
            with self.subTest(path=path.name):
                self.assertIn(link, path.read_text())


class TestValidateBriefHelpers(unittest.TestCase):
    def test_invented_file_path_detected(self) -> None:
        errors = check_no_invented_context(
            "fix login bug",
            "Task:\nFix auth.py login flow.",
        )
        self.assertEqual(errors, ["invented context: auth.py"])

    def test_file_path_from_request_allowed(self) -> None:
        errors = check_no_invented_context(
            "fix auth.py login",
            "Task:\nFix auth.py login flow.",
        )
        self.assertEqual(errors, [])

    def test_parser_accepts_code_fence_without_leading_newline(self) -> None:
        content = """## Bug fix

### 1. sample

**Request:** `fix bug`

```Task:
Fix the bug.
```"""
        examples = parse_examples_markdown(content)
        self.assertEqual(len(examples), 1)
        self.assertEqual(examples[0].kind, "brief")
        self.assertIn("Fix the bug.", examples[0].body)


if __name__ == "__main__":
    unittest.main()
