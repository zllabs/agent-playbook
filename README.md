# Agent Brief

**Turn vague coding requests into concise, structured briefs for coding agents.**

Works with:

- Cursor Project Rules
- Claude Code Skills

Agent Brief turns vague coding requests into concise, structured briefs that reduce ambiguity for coding agents.

It doesn't replace your prompt—it compiles it into a clearer brief.

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

The structure is fixed, but the content adapts to the request.

[More examples →](examples.md) — bug fixes, features, refactors, performance, migrations, debugging.

## Why it works

Good coding agents already know how to write code. They perform better when the developer's intent is clear.

Instead of adding hundreds of words of generic prompt engineering advice, it only fills in the information coding agents commonly need:

- What is the task?
- What context is available?
- What constraints matter?
- How should success be verified?

Agent Brief only adds missing execution details. Everything else comes from the coding agent, repository context, and project instructions.

## When Agent Brief activates

Agent Brief is triggered by the **quality of the request**, not by matching example phrases. It activates when a request lacks sufficient structure for reliable execution.

**Typical requests:**

- fix login bug
- make API faster
- add OAuth
- refactor auth
- investigate memory leak

**Already specific enough:**

- rename `foo()` to `bar()`
- remove unused import
- change timeout to 30 seconds

## Installation

```bash
git clone https://github.com/zllabs/agent-brief.git
cd agent-brief
```

**Cursor** — copy the rule and examples into your project (`.mdc` is the Cursor project-rule format):

```bash
mkdir -p /path/to/your/project/.cursor/rules
cp cursor/rules/agent-brief.md /path/to/your/project/.cursor/rules/agent-brief.mdc
cp examples.md /path/to/your/project/
```

The default rule uses `alwaysApply: true` and self-filters: it applies only when the request is underspecified. Change `alwaysApply` if you prefer Cursor to decide when the rule applies.

**Claude Code** — copy the skill:

```bash
mkdir -p ~/.claude/skills
cp -r claude/skills/agent-brief ~/.claude/skills/
# usage: /agent-brief make API faster
```

**Configuration** (optional):

```bash
cp agent-brief.yaml /path/to/your/project/
```

## Configuration

Create `agent-brief.yaml` in your project root:

```yaml
mode: auto
```

or:

```yaml
mode: review
```

Default is `auto`. Optional debug flag for auto mode:

```yaml
mode: auto
debug: true
```

When `debug: true`, the generated brief is shown before execution.

**How configuration works:** Agent Brief has no runtime. When present, the rule or skill asks the coding agent to read `agent-brief.yaml` from the project root. If the file is unavailable or ignored by the host platform, the default behavior is used.

## Modes

### Auto

Transforms vague requests automatically before execution. Best for daily use.

The generated brief is used internally. It is not shown unless you enable `debug: true` in config.

### Review

Displays the generated brief before execution. Users can review and edit the generated brief before asking the coding agent to continue.

Cursor and Claude Code do not provide native Send, Edit, or Copy actions for a pre-send review step. In review mode, Agent Brief outputs only the brief and waits for your next message — that is the closest available behavior on these platforms.

## Design goals

- Produce briefs expected from an experienced software engineer
- Add structure, not verbosity
- Preserve user intent
- Never invent project-specific details
- Prefer clarification over assumptions
- Keep briefs short

## Tests

Contract tests verify the core design invariants. Run them with:

```bash
python -m tests
```

They check that briefs follow the design goals — required sections, concise length (20–50 words), no fluff, no invented file paths, clarification for ambiguous requests, and no expansion of already-clear requests.

## Scope

One Cursor Rule, one Claude Code Skill, examples, and contract tests. No runtime, no CLI, no framework.
