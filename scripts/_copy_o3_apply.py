#!/usr/bin/env python3
"""COPY-O3 explanation-field rewrites (2026-05-20 council triage follow-up).

For each of the 23 listed rules, locate the existing explanation lede and
replace it with a rewrite that LEADS with the agent consequence. The new
ledes are lifted from the existing fix_prompt openers where they fit
(council Designer + Investor verdict on COPY-O3, formerly EXP-1).

This script is intentionally a single-shot, idempotent textual rewrite:
- Each entry carries the OLD text (exact match) and the NEW text.
- We refuse to rewrite if OLD is missing or non-unique inside the file.
- We do NOT regenerate the YAML via PyYAML / ruamel — the surrounding
  comments and field ordering in each rule are part of the contract.

After running, run `python -c "import yaml; ..."` to confirm every touched
file still parses, and re-run the standard rule-pack tests.
"""

from __future__ import annotations
import pathlib
import sys
import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
RULES_DIR = REPO / "rules"

REWRITES: list[tuple[str, str, str]] = [
    # ----- cognitive_load -----
    (
        "agent_docs.canonical",
        "AGENTS.md at the repo root is the emerging canonical contract between\n"
        "human authors and coding agents (canonical commands, do-not-touch\n"
        "lists, commit conventions). Other formats (.cursorrules, CLAUDE.md,\n"
        ".ai/) help, but a single, well-named file at the root is the most\n"
        "predictable surface for any agent. This rule fires `warn` only when\n"
        "the canonical AGENTS.md is missing; partial coverage by sibling\n"
        "formats is rewarded by the softer `agent_docs.present` rule.\n",
        "Agents landing in a repo need a single, predictable file to read for\n"
        "canonical commands, do-not-touch lists, and commit conventions —\n"
        "AGENTS.md at the repo root is the emerging canonical contract\n"
        "between human authors and coding agents. Other formats\n"
        "(.cursorrules, CLAUDE.md, .ai/) help, but a single, well-named file\n"
        "at the root is the most predictable surface for any agent. This\n"
        "rule fires `warn` only when the canonical AGENTS.md is missing;\n"
        "partial coverage by sibling formats is rewarded by the softer\n"
        "`agent_docs.present` rule.\n",
    ),
    (
        "code.complexity",
        "High cyclomatic complexity means many independent control-flow\n"
        "paths through one function. Agents that try to modify such a\n"
        "function have to consider every path; they make more wrong-branch\n"
        "edits than humans do, who can hold more context in their heads.\n"
        "Functions over CC=15 are the strongest predictor of agent edit\n"
        "errors in a 2026 internal study.\n",
        "Agents editing a high-complexity function have to reason across\n"
        "every independent control-flow path and ship more wrong-branch\n"
        "edits than a human would, who can hold more context in their\n"
        "heads. Cyclomatic complexity is the proxy: functions over CC=15\n"
        "are the strongest predictor of agent edit errors in a 2026\n"
        "internal study.\n",
    ),
    (
        "git.churn_hotspots",
        "Files that are both large *and* frequently edited are the highest-\n"
        "risk surface for an agent: each touch has the most context to\n"
        "re-read and the most history to consider. Splitting them into\n"
        "smaller modules cuts agent error rates more than any other\n"
        "refactor. This rule fires per file that exceeds both the touch and\n"
        "size thresholds; gives `not_measured` on shallow clones and\n"
        "repos with very few commits.\n",
        "Agents editing a churn-hotspot file pay the maximum re-read cost on\n"
        "every touch — the most context to re-read, the most history to\n"
        "consider, the highest chance of colliding with an in-flight change.\n"
        "Files that are both large *and* frequently edited are that surface;\n"
        "splitting them into smaller modules cuts agent error rates more\n"
        "than any other refactor. This rule fires per file that exceeds\n"
        "both the touch and size thresholds; gives `not_measured` on\n"
        "shallow clones and repos with very few commits.\n",
    ),
    (
        "meta.consistency",
        "Drift between what README documents and what the repo actually has\n"
        "is one of the most expensive false starts for an agent: it follows\n"
        "the README, runs into a missing tool, and either reverts or\n"
        "invents a workaround. Common drifts caught here: README mentions\n"
        "pytest but no pytest config exists; README mentions `npm test`\n"
        "but no package.json; README references `make X` for a target that\n"
        "doesn't exist in the Makefile; README documents `npm run X` but\n"
        "the script is missing from package.json; README documents\n"
        "`pip install -e .` but no pyproject.toml/setup.py exists; AGENTS.md\n"
        "/ CLAUDE.md is a placeholder.\n",
        "Agents that follow the README will hit a missing tool or undefined\n"
        "target and either revert or invent a workaround when README\n"
        "documentation drifts from what the repo actually has — one of the\n"
        "most expensive false starts. Common drifts caught here: README\n"
        "mentions pytest but no pytest config exists; README mentions\n"
        "`npm test` but no package.json; README references `make X` for a\n"
        "target that doesn't exist in the Makefile; README documents\n"
        "`npm run X` but the script is missing from package.json; README\n"
        "documents `pip install -e .` but no pyproject.toml/setup.py exists;\n"
        "AGENTS.md / CLAUDE.md is a placeholder.\n",
    ),
    (
        "repo_shape.large_files",
        "Files over 3000 lines or 300 KB exceed an agent's working memory in\n"
        "a single read and force a chunked-reading pattern that loses\n"
        "context across chunk boundaries. This rule excludes lock files,\n"
        "generated data, binary assets, long-form tests, vendored\n"
        "third-party code, and build/template artefacts — which are large\n"
        "but not \"source\" files an agent would meaningfully edit. Thresholds\n"
        "recalibrated in v2.0.1 (3000 lines / 300 KB) from v1.5.0's 1500 /\n"
        "150 KB setting after EXP-2 fire-rate measurement on the v3.2 cohort;\n"
        "see the rule comment block for cohort calibration history.\n",
        "Agents reading a 3000+-line file exceed working memory in a single\n"
        "pass and are forced into chunked reads that lose context across\n"
        "boundaries — files over 3000 lines or 300 KB exceed that budget.\n"
        "This rule excludes lock files, generated data, binary assets,\n"
        "long-form tests, vendored third-party code, and build/template\n"
        "artefacts — which are large but not \"source\" files an agent would\n"
        "meaningfully edit. Thresholds recalibrated in v2.0.1 (3000 lines /\n"
        "300 KB) from v1.5.0's 1500 / 150 KB setting after EXP-2 fire-rate\n"
        "measurement on the v3.2 cohort; see the rule comment block for\n"
        "cohort calibration history.\n",
    ),
    # ----- feedback -----
    (
        "agent_docs.ci_feedback_loop",
        "CI is the main automated feedback channel once an agent pushes a\n"
        "branch. repos that never tell agents to watch workflow results or to\n"
        "treat failing checks as something to fix (not noise) see agents land\n"
        "red PRs, declare \"done,\" and disappear — the same failure mode as\n"
        "missing hooks, only slower. Root `AGENTS.md` should explicitly bind\n"
        "**monitor CI / checks → read failures → fix and iterate** into the\n"
        "agent contract.\n",
        "Agents that push a PR without an explicit contract to watch CI\n"
        "declare \"done\" before checking whether the build went red — the\n"
        "feedback loop is open-circuited and the same failure mode as\n"
        "missing hooks, only slower. CI is the main automated feedback\n"
        "channel once a branch is pushed; the root `AGENTS.md` should\n"
        "explicitly bind **monitor CI / checks → read failures → fix and\n"
        "iterate** into the agent contract.\n",
    ),
    (
        "deploy.smoke_check",
        "When a workflow ships a build to a hosted environment (GitHub Pages,\n"
        "Netlify, Vercel, S3/CloudFront, gh-pages branch, Cloud Run, Fly,\n"
        "Render, Surge), the only feedback signal an agent gets out of the\n"
        "box is \"the deploy step exited 0.\" That is not the same as \"the\n"
        "deployed site actually loads.\" Without a post-deploy smoke check\n"
        "(curl HTTP 200, Playwright/Puppeteer probe, Lighthouse run, etc.),\n"
        "silent prod regressions — broken `base` paths, broken SPA 404\n"
        "fallbacks, asset 404s, missing data files — ship green and the\n"
        "agent declares \"done.\"\n"
        "\n"
        "This rule fires when at least one workflow file references a deploy\n"
        "step, AND no workflow file contains evidence of a smoke check\n"
        "(HTTP probe, e2e tool, or `lighthouse` invocation).\n",
        "Agents reading deploy-workflow output get one signal out of the box\n"
        "— \"deploy step exited 0\" — which is not the same as \"the deployed\n"
        "site loads,\" so silent prod regressions (broken `base` paths,\n"
        "broken SPA 404 fallbacks, asset 404s, missing data files) ship\n"
        "green and the agent declares \"done.\" Without a post-deploy smoke\n"
        "check (curl HTTP 200, Playwright/Puppeteer probe, Lighthouse run,\n"
        "etc.) the agent has no closed-loop verification that the deploy\n"
        "actually shipped a working artefact. This rule catches workflows\n"
        "that ship to hosted environments (GitHub Pages, Netlify, Vercel,\n"
        "S3/CloudFront, gh-pages branch, Cloud Run, Fly, Render, Surge)\n"
        "without a smoke-check step.\n"
        "\n"
        "This rule fires when at least one workflow file references a deploy\n"
        "step, AND no workflow file contains evidence of a smoke check\n"
        "(HTTP probe, e2e tool, or `lighthouse` invocation).\n",
    ),
    (
        "feedback.test_coverage_hint",
        "Coverage configuration (`.coveragerc`, `codecov.yml`, `coveralls.yml`,\n"
        "`pyproject.toml [tool.coverage.*]`) signals that the repo tracks which\n"
        "code is exercised by tests. Agents benefit from knowing what is and\n"
        "isn't tested before making a change, so they can target tests\n"
        "appropriately. Community-contributed demo rule.\n",
        "Agents making a change need to know which lines are covered by\n"
        "tests so they can target new tests appropriately and avoid adding\n"
        "behaviour into an untested path. Coverage configuration\n"
        "(`.coveragerc`, `codecov.yml`, `coveralls.yml`,\n"
        "`pyproject.toml [tool.coverage.*]`) is the signal that the repo\n"
        "tracks this. Community-contributed demo rule.\n",
    ),
    (
        "hooks.configured",
        "Hooks (pre-commit, husky, lefthook, lint-staged, .claude/settings,\n"
        ".cursor/settings) are how a project gives an agent feedback *before*\n"
        "a commit lands rather than after CI fails. A repo that runs format\n"
        "+ lint on every commit cuts the agent's edit/wait/fix loop by an\n"
        "order of magnitude.\n",
        "Agents running an edit/wait/fix loop at CI speed (minutes) bleed\n"
        "time on cosmetic feedback that pre-commit hooks would have caught\n"
        "in seconds — a repo that runs format + lint on every commit cuts\n"
        "that loop by an order of magnitude. Hooks (pre-commit, husky,\n"
        "lefthook, lint-staged, .claude/settings, .cursor/settings) are how\n"
        "the project gives the agent that feedback *before* a commit lands\n"
        "rather than after CI fails.\n",
    ),
    (
        "lint.configured",
        "A configured linter is the difference between an agent's edit being\n"
        "immediately rejected with a clear error and the same edit silently\n"
        "drifting from house style. Even if the linter is permissive, having\n"
        "*a* config tells agents which rules are intentional and which are\n"
        "drift.\n",
        "Agents writing edits without a configured linter silently drift\n"
        "from house style — CI reviewers then spend cycles on cosmetic\n"
        "feedback instead of logic, while the agent never learns which\n"
        "rules were intentional vs. accidental. A configured linter makes\n"
        "that boundary explicit; even a permissive linter config is enough\n"
        "to tell agents which rules are intentional and which are drift.\n",
    ),
    (
        "manifest.detected",
        "A manifest (`pyproject.toml`, `package.json`, `Cargo.toml`,\n"
        "`go.mod`, …) is the contract that tells an agent what the project\n"
        "is, how to install it, and what depends on what. Without one, the\n"
        "agent has to infer everything from filenames and tribal knowledge.\n"
        "This rule looks for a manifest at the repo root or, for monorepos,\n"
        "at depth ≤ 2 (`packages/<name>/pyproject.toml`).\n",
        "Agents need a manifest (`pyproject.toml`, `package.json`,\n"
        "`Cargo.toml`, `go.mod`, …) as the contract telling them what the\n"
        "project is, how to install it, and what depends on what — without\n"
        "one, every action becomes guesswork from filenames and tribal\n"
        "knowledge. This rule looks for a manifest at the repo root or, for\n"
        "monorepos, at depth ≤ 2 (`packages/<name>/pyproject.toml`).\n",
    ),
    (
        "manifest.lockfile_present",
        "A lockfile pins the exact dependency tree the project was last\n"
        "validated against. Without one, `pip install` / `npm install` will\n"
        "resolve different versions on different machines, so an agent that\n"
        "installs deps and runs tests can't trust a green run on its laptop\n"
        "to predict a green run in CI. Some ecosystems (Cargo, Poetry, npm)\n"
        "produce lockfiles automatically; others (bare requirements.txt) do\n"
        "not, and the project has to opt in.\n",
        "Agents running `pip install` / `npm install` / `bundle install`\n"
        "without a lockfile resolve different dependency versions on\n"
        "different machines, so a green test run on the agent's laptop\n"
        "can't predict CI's outcome. A lockfile pins the exact tree the\n"
        "project was last validated against; some ecosystems (Cargo,\n"
        "Poetry, npm) produce one automatically, others (bare\n"
        "requirements.txt) require the project to opt in.\n",
    ),
    (
        "typecheck.configured",
        "A type checker catches whole categories of agent errors (missing\n"
        "fields, wrong arg shapes, stale imports) before they reach runtime.\n"
        "Statically-typed language repos pass automatically; for Python and\n"
        "JS this is opt-in but high-leverage.\n",
        "Agents whose edits ship missing fields, wrong arg shapes, or stale\n"
        "imports rely on runtime — and a partial test run — to catch the\n"
        "regression; a type checker catches whole categories of these\n"
        "errors before runtime. Statically-typed language repos pass\n"
        "automatically; for Python and JS this is opt-in but high-leverage.\n",
    ),
    # ----- flow -----
    (
        "branch_rulesets.configured",
        "Branch protection (or the newer \"branch rulesets\") forces PRs to\n"
        "pass review and CI before they touch the default branch. For an\n"
        "agent-driven workflow this is doubly important: it's the only\n"
        "guard rail against an agent merging something that looks plausible\n"
        "but breaks production. Without it, \"the agent can write to main\"\n"
        "is true, and that's bad.\n",
        "Agents in repos without branch protection can land an agent-opened\n"
        "PR on the default branch without a review or a green CI run — \"the\n"
        "agent can write to main\" is true, and that is the failure mode.\n"
        "Branch rulesets (or the older branch-protection rules) force PRs\n"
        "to pass review and CI before they touch the default branch; for an\n"
        "agent-driven workflow this is doubly important as the only guard\n"
        "rail against an agent merging something that looks plausible but\n"
        "breaks production.\n",
    ),
    (
        "devcontainer.present",
        "A devcontainer / Nix flake / Gitpod config / Vagrantfile lets an\n"
        "agent (or a new contributor) get a reproducible environment without\n"
        "hand-installing system deps. The project that ships one cuts the\n"
        "\"wrong runtime version\" / \"missing system library\" class of failure\n"
        "to zero.\n",
        "Agents in a fresh sandbox hit \"wrong runtime version\" / \"missing\n"
        "system library\" within minutes of bring-up and can't recover\n"
        "headlessly without a reproducible environment definition. A\n"
        "devcontainer / Nix flake / Gitpod config / Vagrantfile lets the\n"
        "agent (or a new contributor) get that environment without\n"
        "hand-installing system deps and cuts the class of failure to zero.\n",
    ),
    (
        "env.example_parity",
        "When code reads from `.env` (or process environment) but no\n"
        "`.env.example` documents the expected keys, headless setup\n"
        "breaks: the agent can't tell which env vars to set before running\n"
        "tests or the app. The full check is \"code references env vars,\n"
        "AND no .env.example-style file exists, AND no equivalent prose\n"
        "documentation (``export FOO=`` snippets in README/CONTRIBUTING) is\n"
        "present.\" All three halves must hold to fire — repos that document\n"
        "env vars in narrative form get credit.\n",
        "Agents reading `os.environ.get(\"API_KEY\")` in code with no\n"
        "`.env.example` (and no equivalent prose in README/CONTRIBUTING)\n"
        "have no way to know API_KEY is required before running tests —\n"
        "headless setup breaks on a missing env var. The full check is\n"
        "\"code references env vars, AND no .env.example-style file exists,\n"
        "AND no equivalent prose documentation (``export FOO=`` snippets in\n"
        "README/CONTRIBUTING) is present.\" All three halves must hold to\n"
        "fire — repos that document env vars in narrative form get credit.\n",
    ),
    (
        "headless.unrunnable_e2e",
        "This is a composite of three already-shipping signals:\n"
        "  - agent_docs.present  (cognitive_load)\n"
        "  - entry_points.detected  (flow)\n"
        "  - test_command.discoverable  (feedback)\n"
        "Individually any one of them is a soft signal. Together — when ALL\n"
        "THREE are absent — the repo is functionally agent-blind: no doc to\n"
        "read, no thing to run, no way to verify. Most healthy repos satisfy\n"
        "at least one; this rule isolates the worst-case intersection.\n"
        "\n"
        "Note: the sub-conditions are written as AND-of-misses (each leaf\n"
        "matcher fires explicitly when its signal is missing), not as OR-of-\n"
        "alternatives mirrored from the source rules. The source rules use\n"
        "OR semantics where the regex clauses default to fire_when=match and\n"
        "go silent when their target file is absent — which makes those rules\n"
        "under-fire on real repos. We avoid that by being explicit here.\n",
        "Agents landing in a repo with no agent-targeted docs, no detected\n"
        "entry point, and no discoverable test command are functionally\n"
        "agent-blind: nothing to read, nothing to run, no way to verify.\n"
        "This rule is the composite of three already-shipping signals —\n"
        "  - agent_docs.present  (cognitive_load)\n"
        "  - entry_points.detected  (flow)\n"
        "  - test_command.discoverable  (feedback)\n"
        "and only fires when ALL THREE are absent. Individually any one of\n"
        "them is a soft signal; together their absence is the worst case.\n"
        "Most healthy repos satisfy at least one.\n"
        "\n"
        "Note: the sub-conditions are written as AND-of-misses (each leaf\n"
        "matcher fires explicitly when its signal is missing), not as OR-of-\n"
        "alternatives mirrored from the source rules. The source rules use\n"
        "OR semantics where the regex clauses default to fire_when=match and\n"
        "go silent when their target file is absent — which makes those rules\n"
        "under-fire on real repos. We avoid that by being explicit here.\n",
    ),
    (
        "setup.command_count",
        "Each command in a README's Setup / Installation section is a place\n"
        "the agent can fail (wrong flag, missing prerequisite, version\n"
        "mismatch). Agents succeed at 1-3 setup commands at near-100% and\n"
        "fall off a cliff after 5. The rule counts distinct shell commands\n"
        "in the setup section's fenced code blocks and shell-prompt lines.\n",
        "Agents chaining 5+ setup commands from a README fall off a cliff\n"
        "after command 3 — each command is a place to fail (wrong flag,\n"
        "missing prerequisite, version mismatch), and 1–3 succeed at\n"
        "near-100% while 5+ collapse. The rule counts distinct shell\n"
        "commands in the setup section's fenced code blocks and shell-\n"
        "prompt lines.\n",
    ),
    (
        "templates.present",
        "Issue templates, PR templates, and CODEOWNERS make agent-opened PRs\n"
        "routable: the right reviewer is auto-assigned, the right metadata\n"
        "fields are filled in, and the project's expectations are explicit.\n"
        "Repos without these get a flood of agent PRs that all look the same\n"
        "and have no obvious reviewer.\n",
        "Agents opening PRs into a repo without issue / PR templates and a\n"
        "CODEOWNERS file all look the same, have no obvious reviewer, and\n"
        "force the project to absorb the routing cost on every PR. Issue\n"
        "templates, PR templates, and CODEOWNERS make those PRs routable:\n"
        "the right reviewer is auto-assigned, the right metadata fields\n"
        "are filled in, and the project's expectations are explicit.\n",
    ),
    (
        "workflow.concurrency_guard",
        "GitHub Actions workflows that push back to their own repo (typical\n"
        "for daily-scan / weekly-rebuild / scheduled data-publishing\n"
        "patterns) without a top-level `concurrency:` block can race\n"
        "themselves. Two scheduled runs (or a manual edit colliding with the\n"
        "cron) lose one set of changes silently — the second `git push` is\n"
        "rejected by the remote, the workflow exits 0, and the data drift is\n"
        "invisible until a human notices stale dashboards.\n"
        "\n"
        "The fix is one block per workflow. For write workflows, prefer\n"
        "`cancel-in-progress: false` so the second run waits for the first\n"
        "rather than tossing its work.\n",
        "Agents (and humans) read \"workflow exited 0\" as success — but two\n"
        "scheduled runs of a self-pushing workflow without a top-level\n"
        "`concurrency:` block race each other: the second `git push` is\n"
        "rejected silently, the workflow exits 0, and one set of changes is\n"
        "lost until a human notices stale dashboards. The pattern bites\n"
        "daily-scan / weekly-rebuild / scheduled data-publishing workflows\n"
        "most often (a manual edit colliding with the cron is the second\n"
        "common trigger).\n"
        "\n"
        "The fix is one block per workflow. For write workflows, prefer\n"
        "`cancel-in-progress: false` so the second run waits for the first\n"
        "rather than tossing its work.\n",
    ),
    # ----- safety -----
    (
        "safety.dependency_automation",
        "Stale dependencies and unscanned third-party code are the most\n"
        "common path from \"agent merged a small change\" to \"merged a CVE\".\n"
        "A repo that declares Dependabot, Renovate, Snyk, FOSSA, Mend, or\n"
        "CodeQL gets PRs / alerts for vulnerable transitive deps and unsafe\n"
        "patterns automatically, so agents reviewing those PRs can act on\n"
        "them rather than re-discovering the issue from scratch.\n",
        "Agents merging small changes against stale, unscanned dependencies\n"
        "are the most common path from \"merged a small change\" to \"merged a\n"
        "CVE\" — transitive deps drift silently and unsafe third-party code\n"
        "accumulates risk. A repo that declares Dependabot, Renovate, Snyk,\n"
        "FOSSA, Mend, or CodeQL gets PRs / alerts for vulnerable transitive\n"
        "deps and unsafe patterns automatically, so agents reviewing those\n"
        "PRs can act on them rather than re-discovering the issue from\n"
        "scratch.\n",
    ),
    (
        "secrets.basic_scan",
        "Tracked files containing AWS access keys, GitHub tokens, Slack\n"
        "tokens, Google API keys, Stripe live keys, or PEM private keys\n"
        "are almost always a credential leak. Even rotating after the fact\n"
        "doesn't help — the leaked secret is in git history forever. This\n"
        "rule catches the high-confidence patterns; for full coverage,\n"
        "layer a tool like `gitleaks` (see safety.gitleaks_config) on top.\n",
        "Agents (and humans) who land a credential into a tracked file are\n"
        "one push away from public git history — rotating the secret after\n"
        "the fact doesn't fully help, because the leaked value is in git\n"
        "forever. This rule catches the high-confidence patterns (AWS\n"
        "access keys, GitHub tokens, Slack tokens, Google API keys, Stripe\n"
        "live keys, PEM private keys); for full coverage, layer a tool like\n"
        "`gitleaks` on top (see `safety.gitleaks_config`).\n",
    ),
    (
        "security.policy_present",
        "A SECURITY.md (or .github/SECURITY.md / docs/SECURITY.md) tells\n"
        "agents and reporters where to send vulnerability disclosures and what\n"
        "the project's response window is. Without it, a coding agent that\n"
        "finds a security issue has no documented escalation path and may\n"
        "default to opening a public issue.\n",
        "Agents that find a security issue with no SECURITY.md (or\n"
        ".github/SECURITY.md / docs/SECURITY.md) have no documented\n"
        "escalation path and may default to opening a public issue,\n"
        "leaking the vulnerability before a fix lands. SECURITY.md tells\n"
        "agents and reporters where to send vulnerability disclosures and\n"
        "what the project's response window is.\n",
    ),
]


def _indent(block: str, prefix: str) -> str:
    return "".join(prefix + line if line.strip() else "\n" for line in block.splitlines(keepends=True))


def find_path_for_rule(rule_id: str) -> pathlib.Path | None:
    for p in RULES_DIR.rglob("*.yaml"):
        try:
            d = yaml.safe_load(p.read_text())
        except Exception:
            continue
        if d.get("id") == rule_id:
            return p
    return None


def main() -> int:
    failures: list[str] = []
    for rid, old, new in REWRITES:
        path = find_path_for_rule(rid)
        if path is None:
            failures.append(f"{rid}: rule file not found")
            continue
        text = path.read_text()
        old_indented = _indent(old, "  ")
        new_indented = _indent(new, "  ")
        n = text.count(old_indented)
        if n == 0:
            failures.append(f"{rid}: old explanation text not found (path={path})")
            continue
        if n > 1:
            failures.append(f"{rid}: old explanation text matched {n} times (path={path})")
            continue
        text2 = text.replace(old_indented, new_indented, 1)
        path.write_text(text2)
        try:
            yaml.safe_load(text2)
        except Exception as e:
            failures.append(f"{rid}: post-rewrite YAML parse failed: {e}")
            continue
        print(f"OK  {rid}  ({path.relative_to(REPO)})")
    if failures:
        print("\nFAILURES:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"\nRewrote {len(REWRITES)} rule explanation ledes (COPY-O3, council 2026-05-20).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
