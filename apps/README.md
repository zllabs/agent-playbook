# Agent Playbook

> **Discover. Visualize. Assemble. Export.**

Describe a software engineering task, get a recommended resource playbook with explainable reasons, explore relationships in the catalog graph, and export JSON.

Agent Playbook is a **metadata catalog and recommendation engine** for AI development resources — Cursor rules, Claude skills, MCP servers, templates, prompts, and more.

## Quick start

### API

```bash
cd apps/api
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Web

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173

### Optional: Ollama reason polish

```bash
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3
```

When set, the API rewrites skill reasons via Ollama. Works without it — template reasons are the default.

## Layout

```
skills/              Local skill packages (auto-discovered via skill.json)
  prompt-refiner/
apps/
  api/               FastAPI + SQLite FTS
  web/               React + Vite + React Flow
data/
  catalog.json       Curated external skills
  custom_skills.example.json  # seed copied to custom_skills.json on first run
```

## API

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/health` | Health + skill count |
| GET | `/api/skills?q=` | Browse/search skills |
| GET | `/api/local-skills` | List local packages from `skills/` |
| GET | `/api/custom-skills` | List user-added custom skills |
| POST | `/api/custom-skills` | Add a custom skill |
| DELETE | `/api/custom-skills/{id}` | Remove a custom skill |
| GET | `/api/edges?ids=` | Edges among skill IDs |
| GET | `/api/local-skills/{id}/source` | Local package README |
| GET | `/api/skills/{id}` | Skill detail |
| POST | `/api/recommend` | `{ "task": "..." }` → Playbook JSON |

## Adding a local skill package

See [skills/README.md](../skills/README.md).

## Tests

```bash
# Package contract tests
python -m tests

# API recommend smoke test
cd apps/api && .venv/bin/python test_recommend.py
```

## License

MIT — see [LICENSE](../LICENSE).
