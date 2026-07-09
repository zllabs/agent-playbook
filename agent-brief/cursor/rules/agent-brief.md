---
description: Compile underspecified coding requests into concise agent briefs (Task, Context, Requirements, Verification). Apply only when the request lacks enough detail to act on directly.
alwaysApply: true
---

# Agent Brief

Transforms vague developer requests into concise coding-agent briefs. Agent Brief does not make prompts longer. It makes developer intent clearer for coding agents.

This is intent compilation: request → agent brief. Add structure only — never role-play, generic advice, or invented project details.

## When to apply

Apply only when the request is **underspecified** — vague enough that a coding agent would need to guess scope, approach, or success criteria.

**Apply:**
- "fix this"
- "fix login bug"
- "make API faster"
- "add authentication"
- "refactor this"

**Do not apply** — execute the request directly:
- "rename function foo to bar"
- "add missing import"
- "change port to 8080"

If the request is already specific, skip this rule entirely.

## Workflow

1. Decide if the request is underspecified. If not, proceed normally.
2. If critical information is missing (e.g. "fix the payment issue" with no error or flow), ask **one** concise question and stop. Do not generate a fake brief.
3. If underspecified but actionable, compile developer intent into a brief structure before acting.
4. Use only context from the user or repository. Never invent project details.

## Brief structure

Use this fixed structure internally (and surface briefly if helpful):

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

Target: 50–150 words. Hard limit: ~200 words.

## Rules

Do not add:
- Role-play ("You are a senior engineer...")
- Generic advice ("Think step by step...", "Follow best practices...")
- Motivational text
- Repeated explanations

Preserve user intent. Add structure only — do not expand scope.

Requirements should be agent-useful only:
- Inspect existing implementation first
- Make minimal changes
- Preserve existing behavior
- Add or update tests if applicable

## Examples

See [examples.md](../../examples.md) for 15+ request → brief transformations.

**Request:** fix login bug → compile brief, then act.

**Request:** rename function foo to bar → execute directly, skip Agent Brief.

**Request:** fix the payment issue → ask one question, do not generate a fake brief.
