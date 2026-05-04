# Contributing rules

Thanks for wanting to add a rule. The bar is low: if your rule names a
concrete agent failure mode it predicts, we'll take it.

## Bar for inclusion

A rule earns a place in the pack when:

- It points at a specific failure mode an agent demonstrably hits.
- It's expressible with the 5 OSS match types (see below). If it
  needs ast-walking or git-history aggregation, it likely belongs in
  the closed engine, not here.
- It can fire on the `agent-readiness-fixtures` repo's `noisy/` or
  `broken/` fixtures (or you'll add a fixture demonstrating it).
- False-positive rate looks tractable. We've already learned this the
  hard way with `repo_shape.large_files`; see
  `agent-readiness-research/research/ideas.md` for FP-tracking history.

## Match types available (RULES_VERSION = 1)

| Type | Use for |
|---|---|
| `file_size` | Files exceeding line/byte thresholds, with glob exclusions |
| `path_glob` | Required or forbidden file/directory patterns |
| `manifest_field` | Missing/present fields in `pyproject.toml` / `package.json` |
| `regex_in_files` | Pattern present/absent in matched files |
| `command_in_makefile` | Makefile target present/missing |

If you need something else, file an issue describing the rule first;
we'll discuss whether it warrants a new match type (which means a
`RULES_VERSION` bump, which is coordinated work) or whether the rule
belongs in the closed engine.

## PR checklist

- [ ] YAML lives at `rules/<pillar>/<rule_id>.yaml`
- [ ] `rules_version: 1` is the first field
- [ ] `id` matches filename
- [ ] `provenance:` field is set. Use
      `agent-readiness/<rule-id>` for native rules; for ports of
      another OSS rule pack, cite the upstream as
      `<owner>/<repo>#<anchor>` (see
      [`LICENSE-NOTICES.md`](LICENSE-NOTICES.md))
- [ ] `explanation` names a concrete agent failure mode (one paragraph)
- [ ] `make validate` passes locally
- [ ] If you added a new fixture, the PR for `agent-readiness-fixtures`
      is linked and merged first
- [ ] If snapshots in `tests/expected/` change, you committed the new ones

## Why provenance is mandatory

Every rule in this pack carries an attribution line in its
`provenance:` field. The schema validator
([`agent-readiness-insights-protocol`](../agent-readiness-insights-protocol/schemas/rule.schema.json))
enforces it; PRs that omit it won't pass `make validate`.

The rule pack is MIT, so anyone can fork and redistribute. The
`provenance:` field exists so a fork is forced to either preserve the
original attribution or replace it with their own — the diff makes
the choice visible. See [`TRADEMARK.md`](TRADEMARK.md) for the
broader policy.
