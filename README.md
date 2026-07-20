# Agent Playbook

> **Discover. Visualize. Assemble. Export.**

A graph-powered platform that **discovers and assembles relevant AI development playbooks** for a software engineering task — by connecting metadata references, explaining recommendations, and exporting a reusable Playbook.

Describe what you want to build. Get a recommended Playbook of Cursor Skills with reasons, a relationship graph, and JSON export.

## Problem

Developers have access to Cursor Skills, MCP servers, rules, prompt libraries, and community repositories — but choosing which resources to use, in what order, and which work together is still manual.

## Why Agent Playbook

Unlike GitHub search, Agent Playbook provides:

- **Task-specific recommendations** — ranked skills matched to your engineering task
- **Explainable reasons** — why each resource is included
- **Resource relationship graphs** — curated edges between related skills
- **Reusable playbook exports** — download `playbook.json` for sharing or tooling

## Demo

**Example task:** Build OAuth authentication using FastAPI

**Home — task entry:**

![Agent Playbook home screen](docs/demo/home.png)

**Result — skill graph:**

![Skill graph showing OAuth & Authentication related to FastAPI Development](docs/demo/graph.png)

**Example Playbook output:** [docs/demo/playbook.example.json](docs/demo/playbook.example.json)

```json
{
  "title": "Build Oauth Authentication Using Playbook",
  "task": "Build OAuth authentication using FastAPI",
  "skills": [
    {
      "id": "oauth-security",
      "title": "OAuth & Authentication",
      "reason": "Matched tags: authentication, oauth.",
      "source_url": "https://github.com/sanjeed5/awesome-cursor-rules-mdc/blob/main/rules-mdc/auth0.mdc",
      "license": "CC0-1.0"
    },
    {
      "id": "fastapi-skill",
      "title": "FastAPI Development",
      "reason": "Matched tags: fastapi.",
      "source_url": "https://github.com/sanjeed5/awesome-cursor-rules-mdc/blob/main/rules-mdc/fastapi.mdc",
      "license": "CC0-1.0"
    }
  ],
  "edges": [
    { "from": "oauth-security", "to": "fastapi-skill", "type": "related_to" }
  ]
}
```

## Quick start

```bash
# API
cd apps/api && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# Web
cd apps/web && npm install && npm run dev
```

Open http://localhost:5173 — see [apps/README.md](apps/README.md) for details.

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/architecture.md](docs/architecture.md) | System design, stack, data model |
| [docs/adding-resources.md](docs/adding-resources.md) | Catalog rules and contribution guide |
| [brainstorm_plan.md](brainstorm_plan.md) | Product scope and MVP definition |

## Repository layout

```
skills/                  # local skill packages (auto-discovered)
apps/
  api/                   # FastAPI backend
  web/                   # React frontend
data/
  catalog.json           # curated external skills + edges
  custom_skills.json     # user-added skills (via UI)
docs/
  architecture.md
  adding-resources.md
  demo/                  # example exports + release screenshots
```

## Packages

Cursor rules and Claude Code skills — no runtime, no CLI. Each package is self-contained.

| Package | Cursor rule | Claude skill | Description |
|---------|-------------|--------------|-------------|
| [prompt-refiner](skills/prompt-refiner/) | [rule.mdc](skills/prompt-refiner/cursor/rule.mdc) | [SKILL.md](skills/prompt-refiner/claude/SKILL.md) | Compile vague requests into structured briefs |

Add a new package under `skills/` — see [skills/README.md](skills/README.md).

## References

Catalog skills link to community and official hubs (see [data/sources.json](data/sources.json)):

| Resource | URL |
|----------|-----|
| Awesome Cursor Rules (MDC) | [github.com/sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc) |
| Cursor Skills docs | [cursor.com/docs/context/skills](https://cursor.com/docs/context/skills) |
| Cursor Rules docs | [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules) |
| Claude Code Skills | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) |
| Agent Skills standard | [agentskills.io](https://agentskills.io) |

See [data/sources.json](data/sources.json) for the full hub list.

## Catalog rules

- **Source URL required** — every catalog entry must link to the canonical resource
- **License required** — SPDX or known license string
- **Attribution required** — author / maintainer field
- **No redistribution of third-party content** — metadata and links only

Details: [docs/adding-resources.md](docs/adding-resources.md)

## Tests

```bash
python -m tests
cd apps/api && .venv/bin/python test_recommend.py
```

## License

MIT — see [LICENSE](LICENSE) if present. Catalog entries retain their upstream licenses; this project stores attribution only.
