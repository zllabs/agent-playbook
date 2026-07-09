---
name: prompt-refiner
description: Compile vague coding requests into concise refined prompts (Task, Context, Requirements, Verification). Use when the user runs /prompt-refiner or asks to structure developer intent for a coding agent.
disable-model-invocation: true
argument-hint: [coding request]
---

# Prompt Refiner

Transforms vague developer requests into concise refined prompts. Prompt Refiner does not make prompts longer. It makes developer intent clearer for coding agents.

This is intent compilation: request → refined prompt. Add structure only — never role-play, generic advice, or invented project details.

## Configuration

Read `prompt-refiner.yaml` in the project root if present. Defaults:

```yaml
mode: auto
```

Supported values: `auto` (default), `review`.

Optional in auto mode:

```yaml
debug: false
```

When `debug: true`, surface the generated brief before continuing (Cursor rule only).

`/prompt-refiner` is always an explicit review step: output only the brief and stop, regardless of `mode`.

## Modes

### Auto (default)

For passive use via the Cursor rule. Transform internally, then execute immediately.

- Do not expose the generated brief unless `debug: true`.
- Continue execution immediately after internal transformation.

For `/prompt-refiner`, output only the brief and stop. Do not execute the task in the same turn.

### Review

For visibility and control.

```
User request → Generate brief → Display brief → Wait for user → Execute
```

- Output **only** the generated brief. No preamble, no before/after comparison, no meta-commentary.
- Do not continue automatically. Wait for the user's next message.
- The brief must be directly editable and easy to copy into another coding agent.
- Claude Code does not provide native Send, Edit, or Copy actions for this step. Output the brief and wait — that is the closest available behavior.

## Workflow

1. Read the request from `$ARGUMENTS` (text after `/prompt-refiner`) or from the user's message.
2. Read `prompt-refiner.yaml` if present. Default `mode: auto`.
3. If critical information is missing (e.g. "fix the payment issue" with no error or flow), ask **one** concise question and stop. Do not generate a fake brief.
4. Otherwise, compile the brief.
5. Output **only** the brief and stop. Do not execute the task or add meta-commentary.
6. In `mode: review`, wait for the user's next message before any follow-up work.

## Brief structure

```
Task:
...

Context:
...

Requirements:
...

Verification:
...
```

Target: 20–50 words. Hard limit: ~200 words.

## Rules

Do not add:
- Role-play ("You are a senior engineer...")
- Generic advice ("Think step by step...", "Follow best practices...")
- Motivational text
- Repeated explanations

Never invent project-specific details (files, modules, services, APIs). Only use context from the user or repository.

Preserve user intent. Add structure only — do not expand scope.

Requirements should be agent-useful only:
- Inspect existing implementation first
- Make minimal changes
- Preserve existing behavior
- Add or update tests if applicable

## Examples

See [examples.md](https://github.com/zllabs/prompt-refiner/blob/main/examples.md) for 15+ request → brief transformations.
