# Playbook Task

Turn vague engineering goals into **playbook-ready task strings** — the kind Agent Playbook (and similar catalogs) rank well.

Works with **Cursor Project Rules** and **Claude Code Skills**. No runtime.

## From vague goal to playbook task

```
I need auth for my API
```

becomes:

```
Build OAuth 2.0 authentication for a FastAPI REST API with JWT sessions and pytest integration tests
```

Paste the result into [Agent Playbook](https://github.com/zllabs/agent-playbook) or use it as a focused coding-agent prompt.

## Installation

### Cursor

```bash
mkdir -p /path/to/your/project/.cursor/rules
cp skills/playbook-task/cursor/rule.mdc /path/to/your/project/.cursor/rules/playbook-task.mdc
```

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r skills/playbook-task/claude ~/.claude/skills/playbook-task
# usage: /playbook-task add auth to my FastAPI app
```

## When it activates

Triggered when the user wants to **phrase a task for resource discovery** or **find Cursor rules / Claude skills** for a project — not for already-specific one-liner edits.

**Applies:** "find skills for my stack", "phrase this for Agent Playbook", "what rules do I need for OAuth"

**Skips:** "rename foo to bar", "fix typo on line 42"

## Output format

One line (or two at most) containing:

- **Verb** — Build, Add, Refactor, Review, Containerize, …
- **Stack** — FastAPI, React, Next.js, Docker, …
- **Scope** — the concrete feature or outcome
- **Optional quality bar** — tests, security review, CI, …

Target: 12–30 words. Do not invent files, modules, or repo details.

## Pair with Prompt Refiner

Use **Playbook Task** to phrase what you're building, then **Prompt Refiner** to compile agent execution briefs once you start coding.
