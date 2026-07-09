"""Brief quality invariant tests."""

from __future__ import annotations

import unittest
from pathlib import Path

from tests.validate_brief import (
    REQUIRED_SECTIONS,
    WORD_HARD_LIMIT,
    WORD_TARGET_MAX,
    WORD_TARGET_MIN,
    check_no_invented_context,
    check_no_role_play_fluff,
    check_structure_compliance,
    check_word_limit,
    check_brief_quality,
    parse_examples_markdown,
    parse_skipped_requests,
    word_count,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = (ROOT / "examples.md").read_text()

REQUIRED_CATEGORIES = {
    "Bug fix",
    "Feature request",
    "Refactor",
    "Performance issue",
    "Migration",
    "Debugging unknown error",
}


class TestBriefInvariants(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.examples = parse_examples_markdown(EXAMPLES)
        cls.briefs = [e for e in cls.examples if e.kind == "brief"]
        cls.clarifications = [e for e in cls.examples if e.kind == "clarification"]
        cls.skipped = parse_skipped_requests(EXAMPLES)

    def test_output_contains_task_section(self) -> None:
        for example in self.briefs:
            with self.subTest(example=example.title):
                self.assertIn("Task:", example.body)

    def test_output_contains_requirements_section(self) -> None:
        for example in self.briefs:
            with self.subTest(example=example.title):
                self.assertIn("Requirements:", example.body)

    def test_output_contains_all_required_sections(self) -> None:
        for example in self.briefs:
            with self.subTest(example=example.title):
                errors = check_structure_compliance(example.body)
                self.assertEqual(errors, [], f"{example.title}: {errors}")

    def test_output_stays_below_word_limit(self) -> None:
        for example in self.briefs:
            with self.subTest(example=example.title):
                count = word_count(example.body)
                self.assertGreaterEqual(count, WORD_TARGET_MIN)
                self.assertLessEqual(count, WORD_TARGET_MAX)
                self.assertLessEqual(count, WORD_HARD_LIMIT)
                self.assertEqual(check_word_limit(example.body), [])

    def test_output_does_not_contain_role_play_fluff(self) -> None:
        for example in self.briefs:
            with self.subTest(example=example.title):
                errors = check_no_role_play_fluff(example.body)
                self.assertEqual(errors, [], f"{example.title}: {errors}")

    def test_output_does_not_invent_context(self) -> None:
        for example in self.briefs:
            with self.subTest(example=example.title):
                errors = check_no_invented_context(example.request, example.body)
                self.assertEqual(errors, [], f"{example.title}: {errors}")

    def test_brief_quality_checks_pass(self) -> None:
        for example in self.briefs:
            with self.subTest(example=example.title):
                errors = check_brief_quality(example.request, example.body)
                self.assertEqual(errors, [], f"{example.title}: {errors}")

    def test_clarification_for_insufficient_information(self) -> None:
        self.assertGreaterEqual(len(self.clarifications), 2)
        for example in self.clarifications:
            with self.subTest(example=example.title):
                self.assertIn("?", example.body)
                for section in REQUIRED_SECTIONS:
                    self.assertNotIn(section, example.body)

    def test_clear_requests_are_not_expanded(self) -> None:
        self.assertGreaterEqual(len(self.skipped), 4)

    def test_examples_cover_required_categories(self) -> None:
        categories = {e.category for e in self.briefs}
        self.assertTrue(
            REQUIRED_CATEGORIES.issubset(categories),
            f"missing categories: {REQUIRED_CATEGORIES - categories}",
        )

    def test_example_count_in_range(self) -> None:
        self.assertGreaterEqual(len(self.briefs), 10)
        self.assertLessEqual(len(self.briefs), 20)


if __name__ == "__main__":
    unittest.main()
