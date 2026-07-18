# Agent instructions for coding agents

Cursor rules and Claude Code skills — no runtime, no CLI. Each package is self-contained and installable on its own.

## Packages

| Package | Cursor rule | Claude skill | Description |
|---------|-------------|--------------|-------------|
| [prompt-refiner](prompt-refiner/) | [rule.mdc](prompt-refiner/cursor/rule.mdc) | [SKILL.md](prompt-refiner/claude/SKILL.md) | Compile vague requests into structured briefs |

## Repository layout

```
prompt-refiner/          # one package per directory
├── README.md            # package docs + install steps
├── examples.md          # optional reference material
├── config.yaml.example  # optional config template
├── cursor/
│   └── rule.mdc         # Cursor project rule
├── claude/
│   └── SKILL.md         # Claude Code skill
└── tests/               # contract tests for this package
```

Add a new package by copying this layout. Keep shared assets (examples, config) inside the package directory.

## Tests

Run all package contract tests:

```bash
python -m tests
```

## Adding a package

1. Create `<name>/` with `cursor/rule.mdc` and/or `claude/SKILL.md`
2. Add `README.md` with install instructions
3. Add `tests/` if the package has verifiable invariants
4. Register it in the table above
