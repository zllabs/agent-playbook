# Adding resources

Agent Playbook indexes **references** to AI development resources — not copies of their content.

## Catalog rules

Every entry in `data/catalog.json` must have:

- **Source URL** — link to the canonical resource (MDC file, docs page, or repo path)
- **License** — SPDX identifier or known license string (`CC0-1.0`, `MIT`, etc.)
- **Attribution** — `author` field naming the maintainer or project
- **No redistribution** — catalog entries are metadata only; do not paste rule bodies, SKILL.md content, or other third-party text into this repo

Edges in `catalog.json` are curated relationships (`requires`, `related_to`) between catalog skill IDs. Both endpoints must exist in the skills array.

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
  "license": "MIT"
}
```

2. Add edges if the skill relates to others already in the catalog.
3. Restart the API (or rely on reload) — `init_db()` reseeds on startup.
4. Verify: `GET /api/skills?q=my-skill` and a recommend query that should match.

Prefer linking to community hubs listed in [data/sources.json](../data/sources.json) (Awesome Cursor Rules MDC, Cursor docs, etc.).

## Add a local skill package

Local packages live under `skills/<id>/` and are auto-discovered via `skill.json`.

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
