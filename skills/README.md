# Skill packages

Local skill packages live here — one directory per skill. The Agent Playbook app auto-discovers them via each package's `skill.json` manifest.

## Layout

```
skills/
├── README.md
└── prompt-refiner/          # example package
    ├── skill.json           # required — metadata for search/recommend
    ├── README.md            # install docs
    ├── examples.md          # optional
    ├── config.yaml.example  # optional
    ├── cursor/
    │   └── rule.mdc
    ├── claude/
    │   └── SKILL.md
    └── tests/               # optional contract tests
```

## Add a new skill

1. Copy an existing package directory (e.g. `prompt-refiner/`) and rename it.
2. Edit `skill.json` — set a unique `id`, `title`, `description`, and `tags`.
3. Update `cursor/rule.mdc` and/or `claude/SKILL.md`.
4. Add `README.md` with install steps.
5. Register the package in the root [README.md](../README.md) table.
6. Restart the API — the skill appears in search and recommendations automatically.

## skill.json

```json
{
  "id": "my-skill",
  "title": "My Skill",
  "description": "What this skill helps with.",
  "tags": ["tag1", "tag2"],
  "ecosystem": "cursor",
  "author": "You",
  "license": "MIT"
}
```

Optional fields: `repo_url`, `source_url` (defaults to this repo on GitHub under `skills/<id>/`).

Catalog metadata lives in [data/catalog.json](../data/catalog.json) and points at external hubs listed in [data/sources.json](../data/sources.json) and the root [README](../README.md#references).
