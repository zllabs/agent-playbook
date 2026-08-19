# Ponytail

Lazy senior dev mode for coding agents — YAGNI, reuse-first, minimal diff. Upstream: [dietrichgebert/ponytail](https://github.com/dietrichgebert/ponytail).

## What it does

Makes your AI agent think like the laziest senior dev in the room. The best code is the code you never wrote.

## Installation

### Cursor

```bash
mkdir -p ~/.cursor/rules
cp skills/ponytail/cursor/rule.mdc ~/.cursor/rules/ponytail.mdc
```

Agent Playbook install writes to `~/.cursor/rules/` only.

## When it activates

On-demand when implementing, refactoring, or choosing architecture — not for pure Q&A or docs tasks.

**Applies:** "keep the diff minimal", "do we already have this?", "simplest way to fix login"

**Skips:** "what is OAuth?", "explain this function"
