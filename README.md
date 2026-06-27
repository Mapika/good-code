# good-code

A Claude Code plugin that teaches an LLM to write **appropriately expressive** backend code
(Python / TypeScript / Go) — fixing over-commenting, over-abstraction, and defensive bloat —
framed as *judgment* (every rule is a WHEN with an explicit when-NOT), not a blunt "write less".
Bundles real before→after examples and a code-quality tripwire scanner.

The plugin lives in [`plugins/good-code/`](plugins/good-code/); see its
[README](plugins/good-code/README.md) for the full rule set, examples, and the
`/good-code:measure` command.

## Install

Via the `mapika` marketplace:

```
/plugin marketplace add Mapika/claude-plugins
/plugin install good-code@mapika
```

Or directly, for local testing:

```
git clone https://github.com/Mapika/good-code
claude --plugin-dir ./good-code/plugins/good-code
```

## License

MIT
