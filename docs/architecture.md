# Architecture

Agent Playbook is a **metadata catalog and recommendation engine** for AI development resources — not a single-ecosystem helper. Cursor rules, Claude skills, MCP servers, AGENTS.md, templates, and prompts are resource types in the same catalog model.

Implementation: FastAPI + SQLite on the backend, React + Vite + React Flow on the frontend.

## Overview

```text
User task (browser)
    → POST /api/recommend
        → SQLite FTS5 search + tag scoring
        → Coalesce connected resource cluster
        → Template reasons (optional Ollama polish)
    → Playbook JSON (resources + edges + reasons)
    → React Result page (list + graph + export)
```

The catalog stores **metadata and attribution only** — title, description, license, tags, canonical URLs, and curated relationship edges. No third-party skill bodies are bundled or redistributed.

## Repository layout

```text
apps/
  api/          FastAPI application
  web/          React SPA (Vite)
data/
  catalog.json  Curated external skill metadata + edges
  sources.json  Hub URLs for documentation links
  custom_skills.json  User-added skills (UI, local file)
skills/         Original local skill packages (skill.json + README); not third-party copies
docs/           OSS documentation
```

## Backend (`apps/api`)

| Module | Role |
|--------|------|
| `main.py` | HTTP routes |
| `db.py` | SQLite schema, FTS5 seed, search, edges |
| `recommend.py` | Rank skills, coalesce cluster, build Playbook |
| `ollama.py` | Optional reason polish |
| `sources.py` | Playbook repo / MDC URL helpers |

**Startup:** `init_db()` drops and reseeds from `catalog.json`, `skills/*/skill.json`, and `custom_skills.json`.

**Search:** Tokenize task text, FTS match, score by tag overlap (generic tags weighted lower), return top matches.

**Recommend:** Select top skills, pull in connected neighbors from edge table, drop isolated orphans when a cluster exists, attach template reasons.

## Frontend (`apps/web`)

| Area | Role |
|------|------|
| `Home.tsx` | Task entry, live skill suggestions |
| `Result.tsx` | Playbook list, checkboxes, add-skill search, export |
| `SkillGraph.tsx` | React Flow graph from Playbook edges |
| `localSkills.ts` | Bundled READMEs for local packages |
| `api.ts` | API client; catalog edges fallback from `catalog.json` |

Vite dev server proxies `/api` → `http://127.0.0.1:8000`.

## Data model

**Skill:** `id`, `title`, `description`, `tags[]`, `ecosystem`, `repo_url`, `source_url`, `author`, `license`, `local?`, `custom?`

**Edge:** `from_id`, `to_id`, `type` ∈ `requires` | `related_to`

**Playbook:** ephemeral per query — `title`, `task`, `skills[]` (with `reason`), `edges[]`, `generated_at`

## API (MVP)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Status + skill count |
| GET | `/api/skills?q=` | Search catalog |
| GET | `/api/local-skills` | List `skills/` packages |
| GET | `/api/local-skills/{id}/source` | README (HTML or `?format=text`) |
| GET | `/api/edges?ids=` | Edges among skill IDs |
| POST | `/api/recommend` | Assemble Playbook |

See [apps/README.md](../apps/README.md) for full route list.

## AI / LLM

No LLM is required. Default reasons are template strings from matched tags. Set `OLLAMA_BASE_URL` to optionally rewrite reasons via a local Ollama model.

## Tests

```bash
python -m tests              # package contract tests
cd apps/api && .venv/bin/python test_recommend.py
```
