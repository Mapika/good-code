---
name: measure
description: >-
  Run the good-code tripwire scanner over files or directories — cyclomatic
  complexity, function length, comment ratio, maintainability index, copy/paste
  duplication, and anti-pattern smells — or compare two trees (e.g. a skill-vs-
  no-skill A/B). Use when asked to measure code quality, check complexity, or
  compare two versions of code. Reports descriptive signals, never targets.
argument-hint: "<paths...>  |  --compare <base-dir> <candidate-dir>  [--json] [--no-dup]"
allowed-tools: Bash
---

# Measure code-quality tripwires

Run the bundled scanner with the user's arguments:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/scripts/measure.py" $ARGUMENTS
```

If no path was given, ask what to measure (a sensible default is the current
working tree or the files just changed).

Then interpret the output for the user, holding to this framing:

- **These are tripwires, not targets.** Per the eval design, code that games any
  single number is *failing*. Never tell the user to "reduce complexity to N" or
  "cut the comment ratio" — read the spread and flag outliers.
- **Alarm conditions worth surfacing:** comment ratio collapsing toward 0 (the
  over-correction into cryptic code), identifier lengths shrinking to noise,
  duplication climbing, a cluster of functions far over the CCN/length thresholds,
  or anti-pattern smell hits (swallowed errors, `any` escape hatches).
- **In `--compare` mode** (the A/B case), report deltas and whether the candidate
  improved without trading away correctness signals — but remember style metrics
  alone never decide a winner; correctness and downstream maintainability do.

**Backends:** the script shells out to `lizard` (complexity) and `radon` (Python
maintainability index) — install with `uv tool install lizard radon` — and to
`jscpd` via `npx` for duplication. Anything missing degrades to a built-in
estimate, and the script prints install hints. PATH is auto-extended with
`~/.local/bin` and `~/go/bin`.
