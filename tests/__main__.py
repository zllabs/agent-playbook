"""Run all package contract tests: python -m tests"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


def _discover_packages(root: Path) -> unittest.TestSuite:
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    for pkg_dir in sorted(root.iterdir()):
        if not pkg_dir.is_dir() or pkg_dir.name.startswith("."):
            continue
        tests_dir = pkg_dir / "tests"
        if not tests_dir.is_dir():
            continue
        sys.path.insert(0, str(tests_dir))
        try:
            for test_file in sorted(tests_dir.glob("test_*.py")):
                module = __import__(test_file.stem)
                suite.addTests(loader.loadTestsFromModule(module))
        finally:
            sys.path.pop(0)
    return suite


if __name__ == "__main__":
    root = Path(__file__).resolve().parent.parent
    result = unittest.TextTestRunner(verbosity=2).run(_discover_packages(root))
    sys.exit(0 if result.wasSuccessful() else 1)
