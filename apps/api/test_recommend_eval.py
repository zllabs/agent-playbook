"""Recommendation quality eval — data-driven cases in eval_cases.json.

Update expectations when catalog ranking intentionally changes:
  1. Edit apps/api/eval_cases.json (expect / forbid lists).
  2. Re-run: cd apps/api && .venv/bin/python test_recommend_eval.py
  3. Note the change in CHANGELOG if behavior is user-visible.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db
from recommend import recommend

CASES_PATH = Path(__file__).resolve().parent / "eval_cases.json"


def main() -> int:
    cases = json.loads(CASES_PATH.read_text())
    db.init_db()

    failed = 0
    for case in cases:
        cid = case["id"]
        pb = recommend(case["task"])
        got = {s.id for s in pb.skills}
        expect = set(case.get("expect", []))
        forbid = set(case.get("forbid", []))

        missing = expect - got
        leaked = forbid & got
        if missing or leaked:
            failed += 1
            print(f"FAIL {cid}: got={sorted(got)}")
            if missing:
                print(f"  missing expect: {sorted(missing)}")
            if leaked:
                print(f"  forbid leaked: {sorted(leaked)}")
        else:
            print(f"OK   {cid}: {sorted(got)}")

    total = len(cases)
    passed = total - failed
    print(f"\n{passed}/{total} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
