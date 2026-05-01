# Agent guide

Conventions for AI coding agents working in this repository.

## Canonical commands

- Validate one rule:    `python -m yaml < rules/cognitive_load/<id>.yaml`
- Validate all rules:   `make validate` (runs `check-jsonschema`)
- Run reference eval:   `make eval` (uses agent-readiness against agent-readiness-fixtures)
- Self-scan:            `agent-readiness scan . --fail-below 75`

The self-scan threshold matches CI (`.github/workflows/ci.yml`). This is
a YAML-only data repo: manifest, lockfile, and typecheck checks aren't
applicable, which puts the realistic ceiling at ~75. Raise the bar in
both AGENTS.md and CI in the same PR if rule additions allow it.

This repo is **pure data**. There is no Python module to import, no
runtime to vendor, no transient state. The Makefile orchestrates
external tools (`check-jsonschema`, `agent-readiness`).

## CI and the feedback loop

**CI is part of the feedback loop.** After you push or update a PR, **monitor GitHub Actions / workflow runs and check results**. When **CI fails**, read the logs, **fix the root cause**, and push follow-up commits. Do not stop while checks are red or ignore failing workflows.

## Schema source of truth

`rule.schema.json` is downloaded from a pinned commit of
`agent-readiness-insights-protocol` and used by CI. We do NOT vendor it
into this repo to avoid drift; instead `make schema-fetch` pulls the
exact ref we're testing against.

### Bumping `PROTOCOL_TAG`

The `PROTOCOL_TAG` env var in `.github/workflows/ci.yml` is pinned to a
40-char commit SHA. Bump it deliberately, in its own PR, when:

1. The upstream protocol cuts a new tagged release (preferred ref).
2. A rule needs a schema feature that only exists past the current pin.

When bumping, switch to the new tag (e.g. `v0.2.0`) rather than another
SHA so the diff is greppable. Do not pin to `main`.

## Adding a rule

1. Pick a pillar (`cognitive_load`, `feedback`, `flow`, `safety`).
2. Create `rules/<pillar>/<id>.yaml` with `rules_version: 1` and the
   required fields. Use an existing rule as a template.
3. Run `make validate` locally. CI also re-runs.
4. If your rule needs a new fixture to exercise, open a PR on
   `agent-readiness-fixtures` first.
5. Regenerate `tests/expected/*.json` locally and commit them in the
   same PR. CI does **not** auto-regenerate snapshots — it diffs the
   committed expected files against fresh `agent-readiness rules-eval`
   output and fails on drift. The canonical regen path is:

   ```bash
   make snapshots
   ```

   `make snapshots` invokes `scripts/regen_snapshots.py`, which assumes
   the sibling-checkout layout (`../agent-readiness/src` on
   `PYTHONPATH` and `../agent-readiness-fixtures/fixtures/{good,
   noisy,broken,monorepo}`). Override either path with
   `--agent-readiness-src` / `--fixtures-root` if your layout differs.
   The script normalises absolute paths to `fixtures/<name>` so the
   committed snapshot diffs cleanly against what CI re-runs.

## Do-not-touch

- `manifest.toml` `rules_version` integer — coordinated bump only.
  Loaders refuse rules whose `rules_version` exceeds their supported
  range; bumping here breaks every consumer that hasn't shipped support.
- `protocol_compat` list — narrowing it is breaking.

## Style

- One rule per file.
- File name matches `id` field.
- `explanation` short and points at an agent failure mode.
- `insight_query` is a free-text hint the engine uses for RAG retrieval.
- Severity is `warn` by default; reserve `error` for safety pillar.
