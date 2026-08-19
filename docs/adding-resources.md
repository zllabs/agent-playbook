# Adding resources

Agent Playbook indexes **references** to AI development resources — Cursor rules, Claude skills, MCP servers, templates, prompts, and similar formats — not copies of their content.

## Third-party resources

Third-party resources remain the intellectual property of their respective authors.

Agent Playbook stores only metadata necessary for discovery, attribution, and recommendation, including titles, descriptions, authors, licenses, canonical URLs, tags, and relationships.

If you are the author of a listed resource and would like it updated or removed, please [open an issue](https://github.com/zllabs/agent-playbook/issues).

## Catalog rules

Every entry in `data/catalog.json` must have:

- **Source URL** — link to the canonical resource (MDC file, docs page, or repo path)
- **License** — SPDX identifier when available; otherwise `Documentation (copyright)` or `Unknown (see source)` for official documentation sites and community hubs
- **Attribution** — `author` field naming the maintainer or project
- **No redistribution** — catalog entries are metadata only. Agent Playbook stores title, description, license, tags, attribution, canonical URLs, and relationships — not rule bodies, SKILL.md content, or other third-party text

Edges in `catalog.json` are curated relationships (`requires`, `related_to`). Endpoints must exist in the catalog **or** as a local package under `skills/`.

## Add an external skill to the catalog

1. Edit [data/catalog.json](../data/catalog.json) — add a skill object:

```json
{
  "id": "my-skill",
  "title": "My Skill",
  "description": "One-line description for search.",
  "tags": ["tag1", "tag2"],
  "ecosystem": "cursor",
  "repo_url": "https://github.com/org/repo",
  "source_url": "https://github.com/org/repo/blob/main/path/to/rule.mdc",
  "author": "org-or-author",
  "license": "MIT",
  "search_hints": [
    "optional intent phrase users might say",
    "another way to describe the same need"
  ]
}
```

`search_hints` are indexed for recommend but not shown in the UI. Use natural phrases a user might type when they do not know the skill name.

2. Add edges if the skill relates to others already in the catalog.
3. Restart the API (or rely on reload) — `init_db()` reseeds on startup.
4. Verify: `GET /api/skills?q=my-skill` and a recommend query that should match.

Prefer linking to community hubs listed in [data/sources.json](../data/sources.json) (Awesome Cursor Rules MDC, Cursor docs, etc.).

When a hub is a **skill repo** (multiple `SKILL.md` packages), add **one catalog entry per skill** — do not stop at a single hub-level row. Each skill needs its own `id`, `source_url` (path to that skill), tags, and license so recommend can surface it on its own.

## Add a local skill package

Local packages live under `skills/<id>/` and are auto-discovered via `skill.json`. **Only add original work or content you have rights to redistribute** — do not copy rules or skills from Cursor Directory, Anthropic, or other catalogs into this folder.

1. Copy an existing package (e.g. `skills/prompt-refiner/`).
2. Edit `skill.json` — unique `id`, title, description, tags, license.
3. Add `cursor/rule.mdc` and/or `claude/SKILL.md` plus `README.md`.
4. Optional: add tests under `tests/`.
5. Register in root [README.md](../README.md) packages table.

See [skills/README.md](../skills/README.md) for the manifest schema.

## Custom skills (UI)

Users can add skills via the web UI — stored in `data/custom_skills.json`. Same attribution rules apply: provide source URL and license when known.

## Pull requests

When contributing catalog entries:

- Confirm the source URL resolves and points at the authoritative resource
- Include license and author exactly as stated upstream
- Do not commit copyrighted content from third-party repositories
- Keep descriptions original and short (for search, not replacement)
