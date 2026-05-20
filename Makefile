.PHONY: schema-fetch validate eval clean test lint snapshots

# Pinned to the same protocol commit CI uses so `make validate` agrees
# with the GitHub Actions run. The Makefile and ci.yml stay in sync via
# code review; bump both when protocol cuts a new tag.
#
# Pinned to protocol v0.4.0 (PR #12) which adds the optional
# `fix_prompt` field on `Rule` (and `Finding`).
PROTOCOL_TAG ?= v0.4.0
SCHEMA_URL = https://raw.githubusercontent.com/harrydaihaolin/agent-readiness-insights-protocol/$(PROTOCOL_TAG)/schemas/rule.schema.json

schema-fetch:
	@echo "Fetching rule.schema.json from agent-readiness-insights-protocol@$(PROTOCOL_TAG)..."
	curl -fsSL -o rule.schema.json $(SCHEMA_URL)

validate: schema-fetch
	@echo "Validating rules against schema..."
	check-jsonschema --schemafile rule.schema.json rules/**/*.yaml

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
