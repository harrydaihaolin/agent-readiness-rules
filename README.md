# agent-readiness-rules

**Open-source rule pack for the agent-readiness scanner.**

This repo holds the YAML rule definitions that
[`agent-readiness`](https://github.com/harrydaihaolin/agent-readiness)
vendors at release time and that the closed insights engine pip-installs
at deploy time. **Pure data — no Python here.** The rule schema lives
in
[`agent-readiness-insights-protocol`](https://github.com/harrydaihaolin/agent-readiness-insights-protocol);
the reference evaluator lives in
[`agent-readiness/src/agent_readiness/rules_eval/`](https://github.com/harrydaihaolin/agent-readiness/tree/main/src/agent_readiness/rules_eval).

## Why a separate repo

Two reasons:

1. **Anyone can contribute a rule.** New noise-pattern catches, new
   anti-pattern detectors, language-specific rules — all welcome via
   PR. You don't need to release a new `agent-readiness` to land one.
2. **Strict versioning.** The `rules_version` integer in
   `manifest.toml` declares which schema this pack conforms to. Loaders
   (in agent-readiness and the engine) refuse rules they don't
   understand, so a future schema change can't silently break old
   installs.

## Layout

```
rules/
  cognitive_load/*.yaml
  feedback/*.yaml
  flow/*.yaml
  safety/*.yaml
manifest.toml         # rules_version + protocol_compat + pack_version
```

## Manifest

```toml
rules_version   = 1            # YAML schema version
protocol_compat = [1]          # PROTOCOL_VERSION values this pack supports
pack_version    = "1.0.0"      # semver of this pack
```

Bump `pack_version`:
- minor on adding rules
- major on removing or breaking-renaming rules

Bump `rules_version`:
- only when the schema in
  `agent-readiness-insights-protocol` bumps `RULES_VERSION`

## Contribute a rule

See [`CONTRIBUTING.md`](./CONTRIBUTING.md). Short version:

1. Add a YAML file under the right pillar dir.
2. CI validates it against the JSON Schema from the protocol package and
   runs the reference evaluator against
   [`agent-readiness-fixtures`](https://github.com/harrydaihaolin/agent-readiness-fixtures).
3. Snapshot updates land with the PR.

## License

MIT.
