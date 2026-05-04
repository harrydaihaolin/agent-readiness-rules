# License notices

The agent-readiness rule pack is MIT-licensed. This file documents
the attribution norms that keep the pack honest as a living
collection of rules.

## Provenance is mandatory

Every rule YAML in this pack carries a `provenance:` field. The
schema validator
([`agent-readiness-insights-protocol`](https://github.com/harrydaihaolin/agent-readiness-insights-protocol/blob/main/schemas/rule.schema.json))
enforces it. The two recognised forms are:

- `agent-readiness/<rule-id>` — native rule authored in this repo.
- `<owner>/<repo>#<anchor>` — port of, or rule inspired by, an
  upstream open-source rule pack. Example:
  `microsoft/agentrc#docs.agents-md`.

When you fork this pack and redistribute one of our rules, the
expectation is:

- Preserve the rule `id` as it was when you took the rule.
- Preserve the `provenance:` line, or replace it with one that
  honestly cites your own modification (e.g.
  `myorg/myfork#derived-from-agent-readiness/<rule-id>`).
- Preserve the rule `explanation` if you keep it byte-for-byte;
  rewrite it if you've materially changed the behaviour.

This is a request grounded in the trademark policy
([`TRADEMARK.md`](TRADEMARK.md)) — not an extension of the MIT
license grant. The point is to make the diff visible: a fork that
strips provenance will say so loudly in code review, and the
community can decide what to do with it.

## Licensed cohort dataset (separate)

The 1000-repo longitudinal cohort dataset, snapshots, and
calibrated LLM-judge labels published alongside this rule pack are
licensed separately and are **not** covered by the MIT license on
the rule YAMLs. See the
[`agent-readiness-leaderboard`](https://github.com/harrydaihaolin/agent-readiness-leaderboard)
repo for the dataset's terms.

## Upstream credits

We seed this section as upstream-derived rules land. As of today the
pack contains no direct ports of third-party rule packs; future
rules ported from other open-source taxonomies (notably
`microsoft/agentrc`) will be listed in this section with their
`provenance:` strings.

If you see a rule on disk that should credit an upstream that this
file doesn't list, open an issue.
