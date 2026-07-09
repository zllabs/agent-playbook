"""Run Agent Brief contract tests."""

from __future__ import annotations

import sys
import unittest


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "report":
        from tests.visual_report import main as generate_report

        generate_report()
        return

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    suite.addTests(loader.discover("tests", pattern="test_*.py"))
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    if result.wasSuccessful():
        from tests.visual_report import generate_reports

        generate_reports()
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
