# Security

Agent Playbook is intended for **local development**. The API has no authentication and writes to local files (`data/custom_skills.json`, `data/playbook.db`).

Do not expose the API to untrusted networks without adding your own access controls.

## Reporting issues

Open a GitHub issue with reproduction steps. For sensitive reports, contact the repository maintainer privately.

## Known local-dev risks

- Unauthenticated `POST /api/custom-skills` and `DELETE /api/custom-skills/{id}`
- SQLite and JSON files are rewritten on API startup and custom-skill mutations
