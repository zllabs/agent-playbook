"""Configuration and mode contract tests."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "agent-brief.yaml"
CURSOR_RULE = (ROOT / "cursor" / "rules" / "agent-brief.md").read_text()
CLAUDE_SKILL = (ROOT / "claude" / "skills" / "agent-brief" / "SKILL.md").read_text()
VALID_MODES = frozenset({"auto", "review"})


def parse_mode_from_config(content: str) -> str:
    match = re.search(r"^mode:\s*(\w+)\s*$", content, re.MULTILINE)
    if not match:
        raise ValueError("missing mode in agent-brief.yaml")
    mode = match.group(1)
    if mode not in VALID_MODES:
        raise ValueError(f"invalid mode: {mode}")
    return mode


def parse_debug_from_config(content: str) -> bool | None:
    match = re.search(r"^debug:\s*(true|false)\s*$", content, re.MULTILINE)
    if not match:
        return None
    return match.group(1) == "true"


class TestConfig(unittest.TestCase):
    def test_config_file_exists(self) -> None:
        self.assertTrue(CONFIG.is_file(), "agent-brief.yaml must exist at project root")

    def test_config_has_valid_mode(self) -> None:
        mode = parse_mode_from_config(CONFIG.read_text())
        self.assertIn(mode, VALID_MODES)

    def test_config_defaults_to_auto(self) -> None:
        mode = parse_mode_from_config(CONFIG.read_text())
        self.assertEqual(mode, "auto")

    def test_parse_mode_rejects_invalid_value(self) -> None:
        with self.assertRaises(ValueError):
            parse_mode_from_config("mode: verbose\n")

    def test_parse_mode_requires_mode_key(self) -> None:
        with self.assertRaises(ValueError):
            parse_mode_from_config("# no mode here\n")

    def test_parse_debug_defaults_to_none_when_absent(self) -> None:
        self.assertIsNone(parse_debug_from_config(CONFIG.read_text()))

    def test_parse_debug_reads_boolean(self) -> None:
        self.assertTrue(parse_debug_from_config("mode: auto\ndebug: true\n"))
        self.assertFalse(parse_debug_from_config("mode: auto\ndebug: false\n"))


class TestModesDocumented(unittest.TestCase):
    def test_cursor_rule_documents_auto_mode(self) -> None:
        self.assertIn("### Auto", CURSOR_RULE)
        self.assertIn("mode: auto", CURSOR_RULE)

    def test_cursor_rule_documents_review_mode(self) -> None:
        self.assertIn("### Review", CURSOR_RULE)
        self.assertIn("`review`", CURSOR_RULE)

    def test_cursor_rule_documents_platform_limitation(self) -> None:
        self.assertIn("does not provide native", CURSOR_RULE)

    def test_claude_skill_documents_review_mode(self) -> None:
        self.assertIn("### Review", CLAUDE_SKILL)

    def test_claude_skill_documents_platform_limitation(self) -> None:
        self.assertIn("does not provide native", CLAUDE_SKILL)

    def test_readme_documents_modes(self) -> None:
        readme = (ROOT / "README.md").read_text()
        self.assertIn("## Modes", readme)
        self.assertIn("### Auto", readme)
        self.assertIn("### Review", readme)
        self.assertIn("## Configuration", readme)


if __name__ == "__main__":
    unittest.main()
