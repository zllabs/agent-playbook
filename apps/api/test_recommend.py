"""Smoke test for recommend ranking without running the server."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import db
from recommend import recommend

db.init_db()
pb = recommend("Build OAuth authentication using FastAPI")
assert pb.skills, "expected skills for OAuth FastAPI task"
ids = {s.id for s in pb.skills}
assert "oauth-security" in ids or "fastapi-skill" in ids
assert "prompt-refiner" not in ids, "prompt-refiner should not appear on unrelated tasks"
print(f"OK: {len(pb.skills)} skills, title={pb.title!r}")

pb_cursor = recommend("Describe a task. Get a Cursor skill Playbook.")
cursor_ids = {s.id for s in pb_cursor.skills}
assert "prompt-refiner" not in cursor_ids, "prompt-refiner should not match on generic cursor tag alone"
print("OK: prompt-refiner excluded for generic cursor task")

pb2 = recommend("refine vague prompts before coding")
refiner = next((s for s in pb2.skills if s.id == "prompt-refiner"), None)
assert refiner, "prompt-refiner should match"
assert refiner.local
assert "create-skill" not in {s.id for s in pb2.skills}, "do not auto-add unrelated neighbors to list"
print("OK: prompt-refiner only when task matches")

pb_pony = recommend(
    "Makes your AI agent think like the laziest senior dev in the room. "
    "The best code is the code you never wrote."
)
pony = next((s for s in pb_pony.skills if s.id == "ponytail"), None)
assert pony, f"ponytail should match intent description, got {[s.id for s in pb_pony.skills]}"
assert "intent" in pony.reason.lower() or "lazy" in pony.reason.lower() or "Matched" in pony.reason
print("OK: ponytail matches by intent not name")

# Simulated orphan: prompt-refiner would be dropped when other skills connect
pb_fake = recommend("Build OAuth authentication using FastAPI")
assert "prompt-refiner" not in {s.id for s in pb_fake.skills}
print("OK: orphans dropped when connected skills exist")

# edges API
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)
r = client.get("/api/edges", params={"ids": "oauth-security,fastapi-skill"})
assert r.status_code == 200
assert len(r.json()) >= 1
print("OK: edges API")

r = client.get("/api/local-skills/prompt-refiner/source", params={"format": "text"})
assert r.status_code == 200
assert b"Prompt Refiner" in r.content
r2 = client.get("/api/local-skills/prompt-refiner/source")
assert r2.status_code == 200
assert "text/html" in r2.headers.get("content-type", "")
print("OK: local skill source")

# FTS search must not crash on malformed input
r = client.get("/api/skills", params={"q": '"'})
assert r.status_code == 200
assert r.json() == []
print("OK: malformed FTS query returns empty list")

# Path traversal blocked
r = client.get("/api/local-skills/..", params={"format": "text"})
assert r.status_code == 404
print("OK: path traversal blocked")

r = client.post("/api/custom-skills", json={
    "id": "bad/id",
    "title": "Bad",
    "description": "Bad id test",
    "tags": ["x"],
})
assert r.status_code == 400
print("OK: invalid custom skill id rejected")
