"""Package structure and artifact contract tests."""

from __future__ import annotations

import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_FILES = (
    "README.md",
    "examples.md",
    "cursor/rules/agent-brief.md",
    "claude/skills/agent-brief/SKILL.md",
)


class TestPackage(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for rel_path in REQUIRED_FILES:
            with self.subTest(path=rel_path):
                self.assertTrue((ROOT / rel_path).is_file(), f"missing {rel_path}")

    def test_cursor_rule_frontmatter(self) -> None:
        content = (ROOT / "cursor/rules/agent-brief.md").read_text()
        self.assertIn("alwaysApply: true", content)
        self.assertIn("Task, Context, Requirements, Verification", content)

    def test_claude_skill_frontmatter(self) -> None:
        content = (ROOT / "claude/skills/agent-brief/SKILL.md").read_text()
        self.assertIn("name: agent-brief", content)
        self.assertIn("disable-model-invocation: true", content)

    def test_readme_positions_product(self) -> None:
        content = (ROOT / "README.md").read_text()
        self.assertIn("I write sloppy requests", content)
        self.assertIn("removes ambiguity between developers and coding agents", content)
        self.assertIn("Design goals", content)

    def test_rule_and_skill_reference_examples(self) -> None:
        for rel_path in (
            "cursor/rules/agent-brief.md",
            "claude/skills/agent-brief/SKILL.md",
        ):
            with self.subTest(path=rel_path):
                content = (ROOT / rel_path).read_text()
                self.assertIn("examples.md", content)


if __name__ == "__main__":
    unittest.main()
