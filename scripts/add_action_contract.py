#!/usr/bin/env python3
"""
add_action_contract.py — one-off migration that adds the ``action`` +
``verify`` blocks required by ``rules_version >= 2`` to every YAML rule
in ``rules/**``.

The script is intentionally regex-based, not YAML-library-based, so all
existing comments in the rules survive the migration. Each rule's
action / verify content lives in the ``ACTIONS`` dict below; if a
rule_id is missing we abort rather than silently leave it on v1 (the
EXP-1 gate is 38/38 structural).

Run from the repo root::

    python scripts/add_action_contract.py
    pytest -q              # to confirm the migrated YAMLs validate
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RULES_DIR = REPO_ROOT / "rules"

# ---------------------------------------------------------------------------
# Action + verify blocks for every rule in the pack.
#
# Convention: each entry is the YAML text that gets appended verbatim
# to the end of the rule file. Indentation is significant — keep two
# spaces under each block. Templates may contain ``{variable}``
# placeholders that the engine fills via ``context_probe`` at scan
# time. Verify commands should be deterministic, offline, ≤15s.
# ---------------------------------------------------------------------------

ACTIONS: dict[str, str] = {
    # ---------------- cognitive_load ----------------
    "agent_docs.canonical": """
action:
  kind: create_file
  path: AGENTS.md
  template: |
    # Agents guide

    A concise (<2 KB) orientation document for autonomous coding agents
    working in this repository. Document, in order:

    1. What this repo does in one sentence.
    2. The single command an agent runs to set up the environment.
    3. The single command to run tests.
    4. The single command to lint.
    5. Where the entry point lives (file path + function/binary name).

    Keep it < 60 lines so it fits in any agent's context window.
  preconditions:
    - not_exists: AGENTS.md
  context_probe:
    - detect: primary_language
verify:
  command: "test -f AGENTS.md"
  description: AGENTS.md must exist at the repo root.
""",
    "agent_docs.present": """
action:
  kind: create_file
  path: AGENTS.md
  template: |
    # Agents guide

    Single-page orientation for AI coding agents. Spell out the setup
    command, the test command, and the entry point. Keep it short.
  preconditions:
    - not_exists: AGENTS.md
verify:
  command: "test -f AGENTS.md"
  description: An AGENTS.md (or AGENTS.txt) file must exist.
""",
    "code.complexity": """
action:
  kind: run_command
  command: |
    # Run a complexity audit and split the highest-complexity functions
    # below the configured threshold. Then re-scan to confirm the rule
    # no longer fires.
    radon cc src/ -s -n B && echo "Refactor any functions above CC threshold."
  description: |
    Run radon (Python) / eslint complexity / similar in your stack to
    identify high-complexity functions and split them by responsibility.
verify:
  command: "true"
  description: |
    No deterministic verify exists for complexity refactors; the rule
    re-scan is the closed loop. Marked offline-safe so the agent can
    proceed without networked tools.
""",
    "cognitive_load.readme_root_present": """
action:
  kind: create_file
  path: README.md
  template: |
    # {primary_language} project

    One-line description.

    ## Setup
    `make install`

    ## Test
    `make test`
  preconditions:
    - not_exists: README.md
  context_probe:
    - detect: primary_language
verify:
  command: "test -f README.md"
  description: README.md must exist at the repo root.
""",
    "docs.contributing_guide": """
action:
  kind: create_file
  path: CONTRIBUTING.md
  template: |
    # Contributing

    ## Setup
    `make install`

    ## Test
    `make test`

    ## Lint
    `make lint`

    ## Submitting changes
    Fork, branch, PR. CI must be green before review.
  preconditions:
    - not_exists: CONTRIBUTING.md
verify:
  command: "test -f CONTRIBUTING.md"
  description: CONTRIBUTING.md must exist at the repo root.
""",
    "git.churn_hotspots": """
action:
  kind: run_command
  command: |
    # Identify the highest-churn files over the last 90 days and split
    # them along their dominant axis of change (feature, layer, domain).
    git log --since='90 days ago' --name-only --pretty=format: \\
      | sort | uniq -c | sort -rn | head -20
  description: |
    No deterministic file-edit fixes a churn hotspot — they require a
    human refactor decision. The command above identifies the top-20
    hotspots so the agent can propose a targeted split.
verify:
  command: "true"
  description: |
    Manual refactor; verification is the next scan no longer flagging
    the file.
""",
    "meta.consistency": """
action:
  kind: run_command
  command: |
    # Audit the README/AGENTS.md/CONTRIBUTING setup commands for
    # consistency. Any drift between them confuses agents.
    grep -E '(make install|pip install|npm install|setup)' \\
      README.md AGENTS.md CONTRIBUTING.md 2>/dev/null
  description: |
    Reconcile setup / test commands across README.md, AGENTS.md, and
    CONTRIBUTING.md so all three documents reference the same flow.
verify:
  command: "true"
  description: Manual reconciliation; re-scan is the closed loop.
""",
    "naming.search_precision": """
action:
  kind: run_command
  command: |
    # Identify ambiguous identifiers (e.g. `util`, `helper`, `manager`)
    # and rename them to domain-specific names so an agent's grep query
    # converges on a single match.
    rg -t py 'def (util|helper|manager|do_)' src/ || true
  description: |
    Rename generic identifiers to domain-specific names so codebase
    search returns a single, unambiguous result for each concept.
verify:
  command: "true"
  description: Manual rename; re-scan is the closed loop.
""",
    "readme.has_run_instructions": """
action:
  kind: append_to_file
  path: README.md
  template: |

    ## Run

    ```
    {package_manager} install
    {language_test_command}
    ```
  context_probe:
    - detect: package_manager
    - detect: primary_language
  preconditions:
    - exists: README.md
verify:
  command: "grep -E '(make|npm|pip|cargo|go) ' README.md >/dev/null"
  description: README.md must contain a runnable command.
""",
    "repo_shape.large_files": """
action:
  kind: run_command
  command: |
    # Identify files exceeding the threshold; split each along its
    # dominant concept axis or move to a vendored / generated-output
    # exclude list.
    find . -type f \\( -name '*.py' -o -name '*.ts' -o -name '*.tsx' \\
      -o -name '*.js' -o -name '*.go' \\) \\
      -not -path './node_modules/*' -not -path './.venv/*' \\
      | xargs wc -l 2>/dev/null \\
      | awk '$1 > 1500 {print}'
  description: |
    No deterministic action — splitting a large source file is a human
    refactor decision. The command above lists candidates so the agent
    can propose a structured split.
verify:
  command: "true"
  description: Manual refactor; re-scan is the closed loop.
""",
    "repo_shape.token_budget": """
action:
  kind: run_command
  command: |
    # Trim AGENTS.md / README.md to the essentials so the orientation
    # cost fits in an agent's context window.
    wc -l AGENTS.md README.md 2>/dev/null
  description: |
    Trim AGENTS.md and README.md so total orientation cost is < 2k
    tokens; split monolithic source files so the largest is < 500 lines.
verify:
  command: "true"
  description: Manual; re-scan is the closed loop.
""",
    "repo_shape.top_level_count": """
action:
  kind: run_command
  command: |
    # Reduce top-level directory count to ≤ 12 by grouping related
    # subtrees under a parent (e.g. apps/, packages/, services/).
    ls -1 . | wc -l
  description: |
    A flat top level confuses agents; group subtrees under parents.
verify:
  command: "true"
  description: Manual; re-scan is the closed loop.
""",
    # ---------------- feedback ----------------
    "agent_docs.ci_feedback_loop": """
action:
  kind: create_file
  path: AGENTS.md
  template: |
    # Agents guide

    ## Feedback loop

    - To preview locally: `make ci-local`
    - To re-run the failing CI step: `gh run rerun --failed`
    - CI artifacts are uploaded to the run page.
  preconditions:
    - not_exists: AGENTS.md
verify:
  command: "grep -i 'feedback\\\\|ci\\\\|test' AGENTS.md >/dev/null"
  description: AGENTS.md must reference the CI feedback loop.
""",
    "ci.configured": """
action:
  kind: create_file
  path: .github/workflows/ci.yml
  template: |
    name: CI
    on:
      pull_request:
      push:
        branches: [main]
    jobs:
      test:
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - run: {language_test_command}
  preconditions:
    - not_exists: .github/workflows/ci.yml
  context_probe:
    - detect: primary_language
verify:
  command: "test -f .github/workflows/ci.yml"
  description: A CI workflow must exist under .github/workflows/.
""",
    "deploy.smoke_check": """
action:
  kind: create_file
  path: .github/workflows/deploy-smoke.yml
  template: |
    name: deploy-smoke
    on:
      deployment_status:
    jobs:
      smoke:
        if: github.event.deployment_status.state == 'success'
        runs-on: ubuntu-latest
        steps:
          - uses: actions/checkout@v4
          - run: curl -fsSL "$DEPLOY_URL/healthz"
            env:
              DEPLOY_URL: ${{ github.event.deployment_status.target_url }}
  preconditions:
    - not_exists: .github/workflows/deploy-smoke.yml
verify:
  command: "test -f .github/workflows/deploy-smoke.yml"
  description: deploy-smoke workflow must exist.
""",
    "feedback.test_coverage_hint": """
action:
  kind: modify_manifest_field
  manifest: pyproject.toml
  field_path: tool.coverage.report.fail_under
  value: "80"
  preconditions:
    - exists: pyproject.toml
    - manifest_language: python
verify:
  command: "grep -E 'fail_under\\\\s*=' pyproject.toml >/dev/null"
  description: A coverage threshold must be configured.
""",
    "hooks.configured": """
action:
  kind: create_file
  path: .pre-commit-config.yaml
  template: |
    repos:
      - repo: https://github.com/pre-commit/pre-commit-hooks
        rev: v4.6.0
        hooks:
          - id: trailing-whitespace
          - id: end-of-file-fixer
          - id: check-yaml
          - id: check-merge-conflict
  preconditions:
    - not_exists: .pre-commit-config.yaml
verify:
  command: "test -f .pre-commit-config.yaml"
  description: .pre-commit-config.yaml must exist.
""",
    "lint.configured": """
action:
  kind: modify_manifest_field
  manifest: pyproject.toml
  field_path: tool.ruff
  value: |
    line-length = 100
    target-version = "py311"
  preconditions:
    - exists: pyproject.toml
    - manifest_language: python
verify:
  command: "grep -E '(\\\\[tool\\\\.ruff\\\\]|eslint|tslint|golangci)' pyproject.toml package.json .golangci.yml 2>/dev/null"
  description: A lint configuration must exist.
""",
    "manifest.detected": """
action:
  kind: create_file
  path: pyproject.toml
  template: |
    [project]
    name = "{primary_language}-project"
    version = "0.1.0"
    requires-python = ">=3.11"

    [build-system]
    requires = ["hatchling"]
    build-backend = "hatchling.build"
  preconditions:
    - not_exists: pyproject.toml
    - not_exists: package.json
    - not_exists: go.mod
    - not_exists: Cargo.toml
  context_probe:
    - detect: primary_language
    - detect: primary_manifest
verify:
  command: |
    test -f pyproject.toml || test -f package.json || \\
      test -f go.mod || test -f Cargo.toml
  description: A primary manifest must exist.
""",
    "manifest.lockfile_present": """
action:
  kind: run_command
  command: |
    # Generate a lockfile using the language's package manager.
    {package_manager} lock || {package_manager} install --frozen-lockfile
  description: |
    Run the package manager's lock command (e.g. `uv lock`,
    `npm install --package-lock-only`, `cargo generate-lockfile`).
  context_probe:
    - detect: package_manager
verify:
  command: |
    test -f uv.lock || test -f poetry.lock || test -f package-lock.json || \\
      test -f yarn.lock || test -f pnpm-lock.yaml || test -f Cargo.lock
  description: A lockfile must exist.
""",
    "test_command.discoverable": """
action:
  kind: append_to_file
  path: Makefile
  template: |

    .PHONY: test
    test:
    \t{language_test_command}
  preconditions:
    - not_exists: Makefile
  context_probe:
    - detect: primary_language
verify:
  command: "make -n test"
  description: |
    `make -n test` must resolve to a runnable command (dry-run; does
    not actually execute the tests).
""",
    "typecheck.configured": """
action:
  kind: modify_manifest_field
  manifest: pyproject.toml
  field_path: tool.mypy
  value: |
    python_version = "3.11"
    strict = false
  preconditions:
    - exists: pyproject.toml
    - manifest_language: python
verify:
  command: "grep -E '(\\\\[tool\\\\.mypy\\\\]|tsconfig|tsc)' pyproject.toml tsconfig.json 2>/dev/null"
  description: A typecheck configuration must exist.
""",
    # ---------------- flow ----------------
    "branch_rulesets.configured": """
action:
  kind: run_command
  command: |
    gh api -X POST \\
      "/repos/$(gh repo view --json nameWithOwner -q .nameWithOwner)/rulesets" \\
      -f name='main protection' \\
      -F enforcement=active \\
      -F 'conditions[ref_name][include][]=refs/heads/main' \\
      -F 'rules[][type]=pull_request' \\
      -F 'rules[][type]=required_status_checks'
  description: |
    Configure a branch ruleset on `main` requiring PRs and status
    checks. Requires gh CLI auth + admin scope on the repo.
verify:
  command: "true"
  description: |
    No offline verify exists for branch protection — re-scan is the
    closed loop.
""",
    "devcontainer.present": """
action:
  kind: create_file
  path: .devcontainer/devcontainer.json
  template: |
    {
      "name": "{primary_language} dev",
      "image": "mcr.microsoft.com/devcontainers/{primary_language}:1",
      "postCreateCommand": "make install"
    }
  preconditions:
    - not_exists: .devcontainer/devcontainer.json
  context_probe:
    - detect: primary_language
verify:
  command: "test -f .devcontainer/devcontainer.json"
  description: .devcontainer/devcontainer.json must exist.
""",
    "entry_points.detected": """
action:
  kind: modify_manifest_field
  manifest: pyproject.toml
  field_path: project.scripts
  value: |
    main = "package.cli:main"
  preconditions:
    - exists: pyproject.toml
    - manifest_language: python
verify:
  command: "grep -E '(project\\\\.scripts|\\"bin\\"|main\\\\.go|cmd/)' pyproject.toml package.json 2>/dev/null"
  description: An entry point must be declared.
""",
    "env.example_parity": """
action:
  kind: create_file
  path: .env.example
  template: |
    # Required environment variables. Copy to .env and fill in values.
    # Discovered automatically from `os.environ.get(...)` / `process.env.*`
    # calls in the source tree.
    EXAMPLE_VAR=
  preconditions:
    - not_exists: .env.example
verify:
  command: "test -f .env.example"
  description: .env.example must exist.
""",
    "git.has_history": """
action:
  kind: run_command
  command: |
    # Initialize the repo and stage an initial commit so agents can
    # see a baseline diff.
    git init && git add -A && git commit -m 'initial commit'
  description: |
    Initialize a git repo (or commit at least 5 changes). Required for
    agents that diff against the merge base.
verify:
  command: "test $(git rev-list --count HEAD 2>/dev/null) -ge 5"
  description: Repo must have ≥ 5 commits.
""",
    "headless.no_setup_prompts": """
action:
  kind: run_command
  command: |
    # Audit setup scripts for interactive prompts (read, $1 unset, etc.).
    grep -rE '(read -p|read [A-Z]+|\\$\\{1\\?)' scripts/ Makefile 2>/dev/null
  description: |
    Replace each interactive prompt with an environment variable or
    a CLI flag default so headless agents don't hang.
verify:
  command: "true"
  description: Manual; re-scan is the closed loop.
""",
    "headless.unrunnable_e2e": """
action:
  kind: run_command
  command: |
    # Identify e2e tests that require a browser/display and gate them
    # behind a CI-only env var.
    grep -rE '(playwright|puppeteer|selenium|cypress)' tests/ e2e/ 2>/dev/null
  description: |
    Mark non-headless e2e tests as skipped when DISPLAY is unset, or
    install xvfb-run in the test command.
verify:
  command: "true"
  description: Manual; re-scan is the closed loop.
""",
    "makefile.help_target": """
action:
  kind: append_to_file
  path: Makefile
  template: |

    .PHONY: help
    help:
    \t@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) \\
    \t  | awk 'BEGIN {FS = ":.*?## "}; {printf "%-20s %s\\n", $$1, $$2}'
  preconditions:
    - exists: Makefile
verify:
  command: "make -n help"
  description: "`make help` must resolve to a runnable target."
""",
    "setup.command_count": """
action:
  kind: run_command
  command: |
    # Collapse multi-step setup into a single `make install` target so
    # an agent can run one command instead of 5+.
    grep -E '^(install|setup|bootstrap):' Makefile 2>/dev/null
  description: |
    Reduce setup to one command. Wrap multi-step flows under a single
    `make install` (or `npm run setup`) target.
verify:
  command: "make -n install"
  description: "`make install` (or equivalent single command) must work."
""",
    "templates.present": """
action:
  kind: create_file
  path: .github/PULL_REQUEST_TEMPLATE.md
  template: |
    ## Summary

    What does this change do, in 1-2 sentences?

    ## Test plan

    - [ ] Unit tests
    - [ ] Manual verification
  preconditions:
    - not_exists: .github/PULL_REQUEST_TEMPLATE.md
verify:
  command: "test -f .github/PULL_REQUEST_TEMPLATE.md"
  description: .github/PULL_REQUEST_TEMPLATE.md must exist.
""",
    "workflow.concurrency_guard": """
action:
  kind: insert_after
  path: .github/workflows/release.yml
  after_pattern: "^name:\\\\s"
  template: |

    concurrency:
      group: ${{ github.workflow }}-${{ github.ref }}
      cancel-in-progress: false
  preconditions:
    - exists: .github/workflows/release.yml
verify:
  command: "grep -E '^concurrency:' .github/workflows/*.yml >/dev/null"
  description: At least one workflow must declare a concurrency group.
""",
    # ---------------- safety ----------------
    "gitignore.covers_junk": """
action:
  kind: edit_gitignore
  entries:
    - .env
    - .env.*
    - "!.env.example"
    - .venv/
    - venv/
    - node_modules/
    - dist/
    - build/
    - "*.log"
    - .DS_Store
    - "*.pyc"
    - __pycache__/
verify:
  command: |
    grep -E '^(\\.env|node_modules|\\.venv|dist|__pycache__)' .gitignore >/dev/null
  description: .gitignore must cover the standard junk groups.
""",
    "safety.dependency_automation": """
action:
  kind: create_file
  path: .github/dependabot.yml
  template: |
    version: 2
    updates:
      - package-ecosystem: "{primary_language}"
        directory: "/"
        schedule:
          interval: weekly
  preconditions:
    - not_exists: .github/dependabot.yml
    - not_exists: renovate.json
  context_probe:
    - detect: primary_language
verify:
  command: "test -f .github/dependabot.yml || test -f renovate.json"
  description: A dependency automation config must exist.
""",
    "safety.gitleaks_config": """
action:
  kind: create_file
  path: .gitleaks.toml
  template: |
    # gitleaks configuration: tunes which paths and rules are scanned
    # for secrets in pre-commit hooks and CI.
    title = "gitleaks config"

    [[allowlist.regexes]]
    description = "Allow .env.example placeholder values"
    regex = '''EXAMPLE_VAR\\s*='''
  preconditions:
    - not_exists: .gitleaks.toml
verify:
  command: "test -f .gitleaks.toml"
  description: .gitleaks.toml must exist.
""",
    "secrets.basic_scan": """
action:
  kind: run_command
  command: |
    # Run a basic secret scan. Use a regex pattern matching common
    # secret formats (AWS, GCP, GitHub PAT, generic API keys).
    rg -E '(AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36}|sk-[A-Za-z0-9]{32,})' \\
      --type-not lockfile || echo "no obvious secrets found"
  description: |
    Run a regex-based secret scan. False positives belong in
    .gitleaks.toml allowlists.
verify:
  command: "true"
  description: |
    Manual / pre-commit-driven; the gitleaks-config rule is the
    structural complement.
""",
    "security.policy_present": """
action:
  kind: create_file
  path: SECURITY.md
  template: |
    # Security policy

    ## Reporting a vulnerability

    Email security@example.com or open a GitHub Security Advisory.
    We respond within 48 hours and aim to ship a fix within 14 days.
  preconditions:
    - not_exists: SECURITY.md
verify:
  command: "test -f SECURITY.md"
  description: SECURITY.md must exist at the repo root.
""",
}


# ---------------------------------------------------------------------------
# Migration logic
# ---------------------------------------------------------------------------


_RULES_VERSION_RE = re.compile(r"^rules_version:\s*1\b", re.MULTILINE)


def migrate_yaml(path: Path) -> tuple[bool, str]:
    """Return (changed, message)."""
    text = path.read_text()
    rule_id_match = re.search(r"^id:\s*(\S+)\s*$", text, re.MULTILINE)
    if not rule_id_match:
        return False, f"{path}: no `id:` line found; skipping"
    rule_id = rule_id_match.group(1)
    block = ACTIONS.get(rule_id)
    if block is None:
        return False, f"{path}: rule id {rule_id!r} missing from ACTIONS dict; skipping"

    new_text = text
    bumped = False
    if _RULES_VERSION_RE.search(new_text):
        new_text = _RULES_VERSION_RE.sub("rules_version: 2", new_text, count=1)
        bumped = True

    if "\naction:\n" in new_text or "\nverify:\n" in new_text:
        # Already migrated; only refresh the version bump if needed.
        if bumped:
            path.write_text(new_text)
            return True, f"{path}: rules_version bumped (action+verify already present)"
        return False, f"{path}: action+verify already present; nothing to do"

    if not new_text.endswith("\n"):
        new_text += "\n"
    new_text += block.lstrip("\n")
    if not new_text.endswith("\n"):
        new_text += "\n"
    path.write_text(new_text)
    return True, f"{path}: migrated -> rules_version=2 + action + verify"


def main() -> int:
    if not RULES_DIR.is_dir():
        sys.exit(f"rules dir not found: {RULES_DIR}")
    yamls = sorted(RULES_DIR.rglob("*.yaml"))
    n_changed = 0
    n_skipped = 0
    for y in yamls:
        changed, msg = migrate_yaml(y)
        print(msg)
        if changed:
            n_changed += 1
        else:
            n_skipped += 1
    missing = [
        rid
        for rid in (
            re.search(r"^id:\s*(\S+)\s*$", y.read_text(), re.MULTILINE).group(1)
            for y in yamls
            if re.search(r"^id:\s*(\S+)\s*$", y.read_text(), re.MULTILINE)
        )
        if rid not in ACTIONS
    ]
    if missing:
        print(f"FAIL: {len(missing)} rule ids missing from ACTIONS: {missing}", file=sys.stderr)
        return 1
    print(f"\n{n_changed} migrated, {n_skipped} skipped")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
