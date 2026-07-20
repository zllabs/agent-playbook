# Agent Playbook

> **Discover. Visualize. Assemble. Export.**

A graph-powered platform that **discovers and assembles relevant AI development playbooks** for a software engineering task — by connecting metadata references, explaining recommendations, and exporting a reusable Playbook.

Describe what you want to build. Get a recommended Playbook of Cursor Skills with reasons, a relationship graph, and JSON export.

Agent Playbook is an open-source project created to help developers discover and assemble reusable AI development resources. It is shared publicly for others to use and build upon.

**Author:** [zhilinglien](https://github.com/zhilinglien) · MIT licensed · personal project ([contributions policy](CONTRIBUTING.md))

## Before & After

Same engineering task — two very different outcomes.

**Task:** *Build OAuth authentication using FastAPI*

![Before manual search vs after Agent Playbook — linked skills in one Playbook](docs/demo/before-after.svg)

| Before | After |
|--------|-------|
| Search GitHub, Cursor Directory, and docs separately | Enter one task → get a ranked Playbook |
| Find FastAPI rules, **miss OAuth and related skills** | **Discover connected skills** via catalog graph |
| No idea how resources relate | **Visual graph** shows `related_to` / `requires` links |
| No reasons, no export | **Explainable reasons** + **playbook.json** export |
| Start coding with gaps in your AI stack | Start with a **linked, explainable resource set** |

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

<img src="docs/demo/home.png" alt="Agent Playbook home screen" width="520">

**Result — skill graph:**

<img src="docs/demo/graph.png" alt="Skill graph showing OAuth & Authentication related to FastAPI Development" width="520">

**Example Playbook output:** [docs/demo/playbook.example.json](docs/demo/playbook.example.json)

```json
{
  "title": "Build OAuth Authentication Using Playbook",
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

Run **both** the API and web app (two terminals):

```bash
# Terminal 1 — API
cd apps/api && python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt && uvicorn main:app --reload --port 8000

# Terminal 2 — Web
cd apps/web && npm ci && npm run dev
```

Open http://localhost:5173 — see [apps/README.md](apps/README.md) for details.

> **Note:** v0.1 is a local-dev tool. See [SECURITY.md](SECURITY.md).

## Documentation

| Doc | Description |
|-----|-------------|
| [docs/architecture.md](docs/architecture.md) | System design, stack, data model |
| [docs/adding-resources.md](docs/adding-resources.md) | Catalog rules (for forks and local use) |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Project status and local development |
| [CHANGELOG.md](CHANGELOG.md) | Release notes |

## Repository layout

```
skills/                  # local skill packages (auto-discovered)
apps/
  api/                   # FastAPI backend
  web/                   # React frontend
data/
  catalog.json           # curated external skills + edges
  custom_skills.example.json  # seed for local custom skills (copied on first run)
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
- **License required** — SPDX identifier, or `See source` for upstream documentation pages
- **Attribution required** — author / maintainer field
- **No redistribution of third-party content** — metadata and links only

Details: [docs/adding-resources.md](docs/adding-resources.md)

## Tests

```bash
python -m tests
cd apps/api && .venv/bin/python test_recommend.py
```

## License

MIT — see [LICENSE](LICENSE). Catalog entries retain their upstream licenses; this project stores attribution only.
