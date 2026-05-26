.PHONY: schema-fetch validate eval clean test lint snapshots

# Pinned to the same protocol commit CI uses so `make validate` agrees
# with the GitHub Actions run. The Makefile and ci.yml stay in sync via
# code review; bump both when protocol cuts a new tag.
#
# Pinned to protocol v0.9.0 which adds the optional `Rule.confidence`
# field (Literal["high","medium","low"], default "medium") — required
# for the per-rule confidence audit shipped in this rules-pack release
# and for the new ontology.gaps_unresolved rule (its match type lives
# in agent-readiness >= 3.2.0). v0.9.0 also adds Gap / Clarification /
# Assumption models (used by the MCP server, not by this pack
# directly). v0.8.3 added the optional Rule.namespace field;
# v0.8.2 added `ontology` to the Pillar enum; v0.8.1 shipped the
# Ontology pillar primitives + Lifecycle + ProposalEnvelope +
# DriftReport. v0.6.0 added Rule.applies_when (language-gating
# selector); v0.4.0 (PR #12) introduced the optional `fix_prompt`
# field on `Rule` (and `Finding`).
PROTOCOL_TAG ?= v0.9.0
SCHEMA_URL = https://raw.githubusercontent.com/harrydaihaolin/agent-readiness-insights-protocol/$(PROTOCOL_TAG)/schemas/rule.schema.json

schema-fetch:
	@echo "Fetching rule.schema.json from agent-readiness-insights-protocol@$(PROTOCOL_TAG)..."
	curl -fsSL -o rule.schema.json $(SCHEMA_URL)

# Prefer a sibling checkout of agent-readiness-insights-protocol when present
# (needed for pillars/match types ahead of a published protocol tag).
_LOCAL_SCHEMA = ../agent-readiness-insights-protocol/schemas/rule.schema.json
SCHEMA_FILE = $(if $(wildcard $(_LOCAL_SCHEMA)),$(_LOCAL_SCHEMA),rule.schema.json)

validate: schema-fetch
	@echo "Validating rules against schema ($(SCHEMA_FILE))..."
	# Use `find` instead of `rules/**/*.yaml` so we pick up files
	# nested arbitrarily deep — bash on Ubuntu (CI) does not enable
	# globstar by default, so `**` collapses to a single-level glob
	# and silently misses `rules/ontology/{schema,validation}/*.yaml`
	# introduced by the A1 namespace split.
	check-jsonschema --schemafile $(SCHEMA_FILE) $$(find rules -name '*.yaml')

eval:
	@echo "Running reference evaluator on agent-readiness-fixtures..."
	# Requires agent-readiness installed and agent-readiness-fixtures cloned alongside.
	agent-readiness rules-eval ../agent-readiness-fixtures/fixtures/good --rules ./rules
	agent-readiness rules-eval ../agent-readiness-fixtures/fixtures/noisy --rules ./rules
	agent-readiness rules-eval ../agent-readiness-fixtures/fixtures/broken --rules ./rules

# `test` runs the canonical sanity check (schema validation). Aliased
# so `agent-readiness scan` and contributor habit both find the entry.
test: validate

lint: validate

snapshots:
	@echo "Regenerating tests/expected/*.json from sibling agent-readiness-fixtures..."
	# Mirrors the normalisation block in .github/workflows/ci.yml so the
	# snapshots committed here diff cleanly against what CI re-runs.
	python3 scripts/regen_snapshots.py

clean:
	rm -f rule.schema.json
