from contextlib import asynccontextmanager
from typing import Optional
import html

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, PlainTextResponse

import db
from models import (
    CreateCustomSkillRequest,
    HealthResponse,
    InstallRequest,
    InstallResponse,
    Playbook,
    PlaybookEdge,
    RecommendRequest,
    Skill,
)
from install_local import install_skills
from ollama import maybe_polish
from recommend import recommend


@asynccontextmanager
async def lifespan(app: FastAPI):
    db.init_db()
    yield


app = FastAPI(title="Agent Playbook API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok", skill_count=db.get_skill_count())


@app.get("/api/skills", response_model=list[Skill])
def list_skills(q: str = "", custom: Optional[bool] = Query(default=None)):
    return [Skill(**s) for s in db.list_skills(q, custom=custom)]


@app.get("/api/local-skills", response_model=list[Skill])
def list_local_skills():
    return [Skill(**s) for s in db.list_local_skills()]


@app.get("/api/local-skills/{skill_id}/source")
def local_skill_source(skill_id: str, format: Optional[str] = Query(default=None)):
    if not db.is_valid_skill_id(skill_id):
        raise HTTPException(status_code=404, detail="Local skill source not found")
    path = db.local_skill_readme_path(skill_id)
    if not path:
        raise HTTPException(status_code=404, detail="Local skill source not found")
    text = path.read_text(encoding="utf-8")
    if format == "text":
        return PlainTextResponse(text, media_type="text/plain; charset=utf-8")
    title = html.escape(skill_id.replace("-", " ").title())
    body = html.escape(text)
    return HTMLResponse(
        f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <style>
    body {{
      font-family: Georgia, "Times New Roman", serif;
      max-width: 42rem;
      margin: 2rem auto;
      padding: 0 1.25rem;
      line-height: 1.65;
      color: #1a1a1a;
      background: #faf9f7;
    }}
    pre {{
      white-space: pre-wrap;
      word-break: break-word;
      font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
      font-size: 0.875rem;
    }}
  </style>
</head>
<body><pre>{body}</pre></body>
</html>"""
    )


@app.get("/api/custom-skills", response_model=list[Skill])
def list_custom_skills():
    return [Skill(**s) for s in db.list_custom_skills()]


@app.post("/api/custom-skills", response_model=Skill, status_code=201)
def add_custom_skill(body: CreateCustomSkillRequest):
    title = body.title.strip()
    description = body.description.strip()
    if not title or not description or not body.tags:
        raise HTTPException(status_code=400, detail="title, description, and tags are required")

    skill_id = (body.id or db.slugify_id(title)).strip()
    if not skill_id:
        raise HTTPException(status_code=400, detail="Could not derive skill id")
    if not db.is_valid_skill_id(skill_id):
        raise HTTPException(
            status_code=400,
            detail="Skill id must use lowercase letters, numbers, and hyphens only",
        )

    skill = {
        "id": skill_id,
        "title": title,
        "description": description,
        "tags": [t.strip().lower() for t in body.tags if t.strip()],
        "ecosystem": body.ecosystem,
        "repo_url": body.repo_url or body.source_url or "",
        "source_url": body.source_url or "",
        "author": body.author,
        "license": body.license,
    }

    try:
        created = db.add_custom_skill(skill)
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))

    return Skill(**created)


@app.delete("/api/custom-skills/{skill_id}", status_code=204)
def delete_custom_skill(skill_id: str):
    if not db.delete_custom_skill(skill_id):
        raise HTTPException(status_code=404, detail="Custom skill not found")
    return None


@app.get("/api/edges", response_model=list[PlaybookEdge])
def list_edges(ids: str = Query("")):
    skill_ids = {i.strip() for i in ids.split(",") if i.strip()}
    raw = db.get_edges_for_skills(skill_ids)
    return [
        PlaybookEdge(from_=e["from_id"], to=e["to_id"], type=e["type"])
        for e in raw
    ]


@app.get("/api/skills/{skill_id}", response_model=Skill)
def get_skill(skill_id: str):
    skill = db.get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return Skill(**skill)


@app.post("/api/playbook/install", response_model=InstallResponse)
def playbook_install(body: InstallRequest):
    """Write selected resources into Cursor or Claude dirs (local API only)."""
    if not body.skills:
        raise HTTPException(status_code=400, detail="At least one skill is required")
    scope = body.scope if body.scope in ("project", "user") else "project"
    ide = body.ide if body.ide in ("cursor", "claude") else "cursor"
    result = install_skills(
        [s.model_dump() for s in body.skills],
        ide=ide,  # type: ignore[arg-type]
        scope=scope,  # type: ignore[arg-type]
        target_dir=body.target_dir.strip() or ".",
        prefer_global_cli=body.global_cli,
    )
    return InstallResponse(**result)


@app.post("/api/recommend", response_model=Playbook)
def recommend_playbook(body: RecommendRequest):
    task = body.task.strip()
    if not task:
        raise HTTPException(status_code=400, detail="Task is required")
    return recommend(task, polish_fn=maybe_polish)
