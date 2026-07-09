---
name: agent-brief
description: Compile vague coding requests into concise agent briefs (Task, Context, Requirements, Verification). Use when the user runs /agent-brief or asks to structure developer intent for a coding agent.
disable-model-invocation: true
argument-hint: [coding request]
---

# Agent Brief

Transforms vague developer requests into concise coding-agent briefs. Agent Brief does not make prompts longer. It makes developer intent clearer for coding agents.

This is intent compilation: request → agent brief. Add structure only — never role-play, generic advice, or invented project details.

## Workflow

1. Read the request from `$ARGUMENTS` (text after `/agent-brief`) or from the user's message.
2. If critical information is missing (e.g. "fix the payment issue" with no error or flow), ask **one** concise question and stop. Do not generate a fake brief.
3. Otherwise, output **only** the agent brief. No preamble, no before/after comparison, no meta-commentary.

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

Target: 50–150 words. Hard limit: ~200 words.

## Rules

Do not add:
- Role-play ("You are a senior engineer...")
- Generic advice ("Think step by step...", "Follow best practices...")
- Motivational text
- Repeated explanations

Never invent project details. Only use context from the user or repository.

Preserve user intent. Add structure only — do not expand scope.

Requirements should be agent-useful only:
- Inspect existing implementation first
- Make minimal changes
- Preserve existing behavior
- Add or update tests if applicable

## Examples

See [examples.md](../../examples.md) for 15+ request → brief transformations.
