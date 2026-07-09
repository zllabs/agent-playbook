# Agent Brief

**I write sloppy requests. This makes my agent understand me better.**

Agent Brief turns vague coding requests into short, structured briefs. It removes ambiguity between developers and coding agents — without padding prompts with role-play or generic advice.

## Before and after

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

[More examples →](examples.md) — bug fixes, features, refactors, performance, migrations, debugging.

## Install

**Cursor** — passive rule, no `@` mention needed:

```bash
mkdir -p .cursor/rules
cp cursor/rules/agent-brief.md .cursor/rules/agent-brief.mdc
```

**Claude Code** — explicit skill:

```bash
mkdir -p ~/.claude/skills
cp -r claude/skills/agent-brief ~/.claude/skills/
# usage: /agent-brief make API faster
```

Underspecified requests get compiled (`fix login bug`). Specific ones are left alone (`rename function foo to bar`).

## Design goals

- Add structure, not verbosity
- Preserve user intent
- Never invent context
- Prefer clarification over assumptions
- Keep briefs short

Agents already receive system instructions, repo context, and project rules. Agent Brief only adds missing execution details.

## Tests

Contract tests validate that briefs follow these rules — not agent task completion.

```bash
python -m tests
```

```
Ran 16 tests in 0.002s

OK
```

| Invariant | What it checks |
|-----------|----------------|
| Structure | Task, Context, Requirements, Verification present |
| Conciseness | Briefs stay within word limits |
| No fluff | No role-play or generic advice |
| No invented context | No fabricated paths or details |
| Clarification | Ambiguous requests ask a question, not a fake brief |
| Skip clear requests | Specific requests are not expanded |

![Contract tests by invariant](tests/reports/contract-tests.svg)

![Example briefs by category](tests/reports/example-categories.svg)

![What Agent Brief adds](tests/reports/brief-structure.svg)

Regenerate charts: `python -m tests report`

## Scope

v1 is one Cursor rule, one Claude skill, examples, and contract tests. No CLI, extension, prompt library, or evaluation pipeline.
