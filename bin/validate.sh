#!/usr/bin/env bash
# Validate every rule under rules/ against the current rule.schema.json
# fetched from agent-readiness-insights-protocol. Mirrors what CI does;
# kept here so contributors can run the same check locally.
#
# Usage: bin/validate.sh [PROTOCOL_TAG]   (default v0.1.0)

set -euo pipefail

PROTOCOL_TAG="${1:-v0.1.0}"
SCHEMA_URL="https://raw.githubusercontent.com/harrydaihaolin/agent-readiness-insights-protocol/${PROTOCOL_TAG}/schemas/rule.schema.json"
TMP_SCHEMA="$(mktemp -t rule.schema.XXXXXX.json)"
trap 'rm -f "$TMP_SCHEMA"' EXIT

if ! command -v check-jsonschema >/dev/null 2>&1; then
  echo "check-jsonschema not installed (pip install check-jsonschema)" >&2
  exit 2
fi

curl -fsSL -o "$TMP_SCHEMA" "$SCHEMA_URL"
shopt -s globstar
check-jsonschema --schemafile "$TMP_SCHEMA" rules/**/*.yaml
echo "OK: every rule conforms to ${PROTOCOL_TAG}/rule.schema.json"
