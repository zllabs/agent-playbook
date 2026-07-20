# Agent Playbook

> **Discover. Visualize. Assemble. Export.**

*A graph-powered platform that recommends the best AI playbooks for a development task by discovering, connecting, and packaging reusable AI resources.*

---

## Vision

Agent Playbook helps developers quickly find the right combination of AI resources for a software engineering task.

Instead of manually searching GitHub, community repositories, and official registries, developers simply describe what they want to build.

Agent Playbook discovers the most relevant resources, explains why they are recommended, visualizes their relationships, and exports a reusable Playbook.

---

## Problem

Developers have access to Cursor Skills, MCP Servers, Rules, prompt libraries, and community repositories — but choosing which resources to use, in what order, and which work together is still manual.

Agent Playbook simplifies that.

---

## Non Goals

Agent Playbook is **NOT**

* a Skill marketplace
* a package manager
* a workflow execution engine
* another AI coding assistant

It is a recommendation and discovery platform.

---

## MVP Scope (v0.1)

### One job

Given a natural-language engineering task, assemble one recommended Playbook of **Cursor skills** (metadata references only), show why each item is included, show a simple relationship graph, export `playbook.json`.

### In scope

| Feature | Implementation |
|---------|----------------|
| Cursor skills only | Curated `data/catalog.json` |
| Keyword / FTS search | SQLite FTS5 + tag scoring |
| Assembled Playbook per query | `POST /api/recommend` |
| Template reasons | Tag-based; optional Ollama polish |
| Graph visualization | React Flow from curated edges |
| Export | Client download of `playbook.json` |
| Attribution | License + source URL per skill |

### Out of scope (deferred)

* Claude Code, MCP, Rules ecosystems
* Live GitHub crawling
* Semantic embeddings
* Pre-authored Playbook marketplace
* OpenRouter / Gemini / OpenAI
* NetworkX, Neo4j
* ZIP bundles, installers
* Ratings, reviews, compatibility engine

---

## User Flow

```text
Enter task → FTS match skills → Rank + attach reasons
         → Assemble Playbook → Show list + graph → Export JSON
```

---

## Architecture

```text
apps/
  api/          FastAPI + SQLite
  web/          React + Vite + React Flow
data/
  catalog.json  Curated skill metadata seed
```

**Stack:** Python 3.9+, FastAPI, SQLite FTS5, React, TypeScript, React Flow.

**AI:** No LLM required by default. Optional Ollama (`OLLAMA_BASE_URL`) polishes reasons only.

---

## Data Model

**Skill:** `id`, `title`, `description`, `tags[]`, `ecosystem`, `repo_url`, `source_url`, `author`, `license`, `version?`

**Edge:** `from_id`, `to_id`, `type` ∈ `requires` | `related_to`

**Playbook** (ephemeral, per query):

```json
{
  "title": "FastAPI OAuth Playbook",
  "task": "Build OAuth authentication using FastAPI.",
  "skills": [
    { "id": "...", "title": "...", "reason": "...", "source_url": "...", "license": "..." }
  ],
  "edges": [{ "from": "...", "to": "...", "type": "related_to" }],
  "generated_at": "..."
}
```

A Playbook references resources; it does not bundle third-party content.

---

## UI (two screens)

### Home — task entry

* Brand: **Agent Playbook**
* Tagline: “Describe a task. Get a Cursor skill Playbook.”
* Large textarea + **Assemble** button
* Example chips

### Result — Playbook

* Playbook title + original task
* Skill list with reason, license, source link
* React Flow graph (click node → focus list row)
* **Export JSON**, **New task**

---

## API

1. `GET /api/health`
2. `GET /api/skills?q=`
3. `POST /api/recommend` — `{ "task": "..." }`
4. `GET /api/skills/{id}`

---

## Legal / OSS

* MIT license for this project's code
* Catalog stores attribution only; no redistributed skill bodies
* UI shows license + source link per skill

---

## Definition of Done (v0.1)

1. Seed catalog loads into SQLite on API start
2. User enters a task and gets a Playbook
3. Each skill has a reason + attribution
4. Graph shows skills with curated edges
5. Export downloads `playbook.json`
6. Works with Ollama stopped
7. `prompt-refiner` appears in catalog and can be recommended

---

## Future Scope

* Claude Code, MCP, Rules support
* Semantic embeddings
* Live GitHub metadata indexing
* Community Playbooks
* OpenRouter / Gemini / OpenAI providers
* Compatibility and dependency analysis
* Ratings and reviews
* ZIP export with README snippet

---

## References

Inspired by Graph of Skills, Skilldex, OpenSkills, OmniSkill, Cursor Skills, Claude Code Skills, Model Context Protocol, React Flow, and Obsidian Graph View.

Each external resource should be properly acknowledged and linked in project documentation.

---

## Ultimate Goal

> **"I know what I want to build. What is the best AI Playbook to help me build it?"**

The project succeeds when discovering, understanding, and assembling AI resources becomes significantly easier than manually searching repositories, while remaining respectful of the open-source ecosystem.
