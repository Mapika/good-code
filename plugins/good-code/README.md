# good-code

A Claude Code plugin that teaches **appropriately-expressive backend code** in
Python, TypeScript, and Go — and a scanner to measure it.

It targets the characteristic failure of generated code: *miscalibrated
expressiveness* (over-commenting, narrating the obvious, abstracting for a single
caller, defensive bloat). Unlike "write less / minimal comments" style guides,
**every rule is a judgment with an explicit when-NOT guard**, so it doesn't
overcorrect into cryptic, under-documented code. The target is code a thoughtful
reviewer couldn't tell was machine-written.

## What's inside

```
good-code/
├── .claude-plugin/plugin.json
├── skills/
│   ├── good-code/
│   │   ├── SKILL.md        # always-on guidance: 32 rules in 7 themes, each judgment-framed
│   │   ├── REFERENCE.md    # full rationale, sources, 6 adjudicated canon conflicts (on demand)
│   │   └── examples/       # 96 before→after pairs (Py/TS/Go); INDEX.md + per-rule files
│   └── measure/
│       └── SKILL.md        # /good-code:measure — run the tripwire scanner
├── scripts/
│   └── measure.py          # complexity, comment ratio, MI, duplication, anti-pattern smells
└── README.md
```

## The two skills

- **`good-code`** — fires when writing, editing, or reviewing backend code, or on
  "clean up / refactor" requests. Loads the condensed rules; pulls in `examples/`
  and `REFERENCE.md` on demand.
- **`/good-code:measure`** — runs `scripts/measure.py` on files/dirs, or
  `--compare <base> <cand>` to diff two trees. Reports tripwires (descriptive
  signals), never targets.

## Install / test locally

```bash
claude --plugin-dir ./good-code     # load for one session
/reload-plugins                      # after edits
claude plugin validate ./good-code   # check manifest + skills
```

Scanner backends (optional — the script degrades gracefully and prints hints):

```bash
uv tool install lizard radon         # cross-language complexity + Python MI
# duplication uses jscpd via npx (needs node); no install step required
```

## How it was built

Distilled from clean long-lived OSS backends and the engineering-book canon, then
adversarially critiqued so every rule teaches *when*, not a direction. Notably the
"many tiny functions" advice from *Clean Code* was resolved against, in favor of
Ousterhout's deep modules. The 96 examples were mined per-rule and **source-
verified**: only pairs whose cited repo URL was fetched and confirmed are tagged
`sourced` (Flask, httpx, requests, Puppeteer, nodebestpractices, Google
eng-practices); the rest are honest, idiomatic `synthetic` pairs with no false
attribution.

## Status

v0.3.0. Evaluated with skill-vs-no-skill A/B tests (same model per arm; blind judge from a
different model family). Directional, small-scale, LLM-judged — not proof.

**Where it helps (measured):** on open-ended / greenfield tasks it curbs structural
over-abstraction (e.g. an "implement a notification system" prompt: roughly halved class count and
~40% fewer lines on a weak model), stays correctness-safe, is judged more maintainable, and
generalizes to held-out tasks without overcorrecting into cryptic / under-built code.

**Where it doesn't (also measured, honestly):** on *precisely-specified* tasks (a ticket with exact
behavior), models write direct code regardless and the skill changes little. A behavior-gated
extend/fix test showed no measurable extensibility gain at small scale, and the
maintainability-at-scale claim is not reachable with such tasks. v0.3 softens a v0.2 "structure
tax" where the skill could nudge a weak model into more structure than a small precise task needs.

**Use it for:** vague / greenfield backend work, refactors, and "clean this up" requests.
Limitations: small N, LLM (not human) judge, single-file tasks.
