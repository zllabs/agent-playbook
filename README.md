# Agent instructions for coding agents

Cursor rules and Claude Code skills — no runtime, no CLI. Each package is self-contained and installable on its own.

## Agent Playbook app

Describe a task, get a ranked Cursor skill Playbook with graph visualization and JSON export.

```bash
# See apps/README.md for full setup
cd apps/api && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && uvicorn main:app --reload --port 8000
cd apps/web && npm install && npm run dev
```

Open http://localhost:5173

## Packages

| Package | Cursor rule | Claude skill | Description |
|---------|-------------|--------------|-------------|
| [prompt-refiner](skills/prompt-refiner/) | [rule.mdc](skills/prompt-refiner/cursor/rule.mdc) | [SKILL.md](skills/prompt-refiner/claude/SKILL.md) | Compile vague requests into structured briefs |

## Repository layout

```
skills/                  # local skill packages (auto-discovered by the app)
├── README.md
└── prompt-refiner/      # one package per directory
    ├── skill.json       # metadata manifest
    ├── README.md
    ├── examples.md
    ├── config.yaml.example
    ├── cursor/rule.mdc
    ├── claude/SKILL.md
    └── tests/

apps/
  api/                   # FastAPI backend
  web/                   # React frontend

data/
  catalog.json           # curated external skills
  custom_skills.json     # user-added skills (via UI)
```

Add a new package under `skills/` — see [skills/README.md](skills/README.md).

## References

Catalog skills link to these community and official hubs (see also [data/sources.json](data/sources.json)):

| Resource | URL | Notes |
|----------|-----|-------|
| Awesome Cursor Rules (MDC) | [github.com/sanjeed5/awesome-cursor-rules-mdc](https://github.com/sanjeed5/awesome-cursor-rules-mdc) | Community `.mdc` rules per library/framework |
| Cursor Official Plugins | [github.com/cursor/plugins](https://github.com/cursor/plugins) | Official rules, skills, agents, MCP |
| Cursor Skills docs | [cursor.com/docs/context/skills](https://cursor.com/docs/context/skills) | Authoring Agent Skills |
| Cursor Rules docs | [cursor.com/docs/context/rules](https://cursor.com/docs/context/rules) | Project rules |
| Cursor Bugbot | [cursor.com/docs/bugbot](https://cursor.com/docs/bugbot) | PR review |
| Cursor Directory | [cursor.directory](https://cursor.directory) | Community rules & MCP |
| Claude Code Skills | [code.claude.com/docs/en/skills](https://code.claude.com/docs/en/skills) | Claude Code skills guide |
| Anthropic Skills | [github.com/anthropics/skills](https://github.com/anthropics/skills) | Example Claude skills |
| Agent Skills standard | [agentskills.io](https://agentskills.io) | Open SKILL.md standard |

Local packages under `skills/` are indexed from each package's `skill.json` and link to this repository.

## Tests

Run all package contract tests:

```bash
python -m tests
```

## Adding a package

1. Create `skills/<name>/` with `skill.json`, `cursor/rule.mdc` and/or `claude/SKILL.md`
2. Add `README.md` with install instructions
3. Add `tests/` if the package has verifiable invariants
4. Register it in the table above
