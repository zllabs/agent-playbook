---
name: playbook-task
description: Rewrite vague engineering goals into playbook-ready task strings for AI dev resource discovery. Use when the user runs /playbook-task or asks to phrase a task for Agent Playbook or find Cursor rules/skills.
disable-model-invocation: true
argument-hint: [engineering goal]
---

# Playbook Task

Turn vague engineering goals into **playbook-ready task strings** — concise lines that resource catalogs can rank and match.

This is task phrasing for discovery: vague goal → specific task line. Add stack terms and scope only — never invent project files or architecture.

## When to apply

Apply when the user wants to **find AI dev resources** or **phrase a task for a playbook/catalog**.

**Apply:** "I need auth for my API", "find skills for React", "phrase this for Agent Playbook"

**Skip:** already-specific one-liner edits (rename, import fix, port change)

## Workflow

1. Identify the engineering outcome (feature, refactor, review, deploy, test, …).
2. If critical stack context is missing, ask **one** concise question and stop.
3. Output a single playbook-ready task string. Optional second line: suggested search tags (comma-separated).

## Task string rules

Include when known:

- **Verb** — Build, Add, Refactor, Review, Containerize, Write, Set up, …
- **Stack** — FastAPI, React, Next.js, SQLite, Docker, GitHub Actions, …
- **Scope** — the concrete feature or outcome
- **Quality bar** — pytest, E2E, security review, CI — only if implied

Target: 12–30 words. Hard limit: ~50 words.

Do not invent repo paths, modules, or team process.

## Examples

**Input:** I need auth for my API  
**Output:** Build OAuth 2.0 authentication for a FastAPI REST API with JWT sessions and pytest integration tests

**Input:** dockerize everything  
**Output:** Containerize the app with Docker and docker-compose for local development and production deploy

## After output

For `/playbook-task`, output only the task string (and optional tags). Stop — do not implement unless asked.
