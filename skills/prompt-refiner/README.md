# Prompt Refiner

Turn vague coding requests into concise, structured briefs for coding agents.

Works with **Cursor Project Rules** and **Claude Code Skills**. No runtime — the agent reads instructions and optional config.

## From request to brief

```
fix login bug
```

becomes:

```
Task:
Fix the login bug.

Context:
Investigate the authentication flow.

Requirements:
Make minimal changes. Preserve behavior. Add tests if applicable.

Verification:
Run relevant tests.
```

[More examples →](examples.md)

## Installation

### Cursor

Install globally (recommended — loads in every project without reinstall):

```bash
mkdir -p ~/.cursor/rules
cp skills/prompt-refiner/cursor/rule.mdc ~/.cursor/rules/prompt-refiner.mdc
cp skills/prompt-refiner/examples.md ~/   # optional
cp skills/prompt-refiner/config.yaml.example /path/to/your/project/prompt-refiner.yaml   # optional per-project
```

Agent Playbook install writes to `~/.cursor/rules/` only (not the project dir).

The rule uses `alwaysApply: false` and self-filters — it only runs on underspecified requests.

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r skills/prompt-refiner/claude ~/.claude/skills/prompt-refiner
# usage: /prompt-refiner make API faster
```

## Configuration

Optional `prompt-refiner.yaml` in your project root:

```yaml
mode: auto   # or review
debug: false # auto mode only; show brief before executing
```

If the file is missing or unreadable, defaults apply.

## When it activates

Triggered by **request quality**, not keyword matching.

**Applies:** fix login bug, make API faster, add OAuth, refactor auth

**Skips:** rename `foo()` to `bar()`, remove unused import, change timeout to 30s

## Modes

| Mode | Behavior |
|------|----------|
| `auto` | Compile internally, execute immediately. Brief hidden unless `debug: true`. |
| `review` | Output brief only, wait for user before continuing. |

## Design goals

- Add structure, not verbosity (target 20–50 words)
- Preserve user intent; never invent project details
- Prefer one clarifying question over a fake brief
- Skip already-specific requests

## Tests

```bash
python -m tests
```

Contract tests live in `skills/prompt-refiner/tests/` and verify brief structure, length, and artifact consistency.
