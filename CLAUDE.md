# CLAUDE.md — agent-readiness-rules

This file is the Claude / Claude Code companion to AGENTS.md.
**Read AGENTS.md first** — it is the canonical source of conventions,
canonical commands, and do-not-touch paths. This file only lists tips
that are specifically useful when Claude is the operator.

## Default loop

1. Read AGENTS.md before any non-trivial change.
2. Run `make validate` before opening a PR.
3. Keep diffs scoped to one logical change. Prefer many small PRs over
   one large one.

## What Claude should never do here

- Commit secrets. The repo's `.gitignore` covers `.env`; honour it.
- Touch generated, vendored, or hardcoded-do-not-touch directories
  listed in AGENTS.md.
- Skip pre-commit hooks. If a hook fails, fix the underlying issue and
  re-stage; do not pass `--no-verify`.

## Headless contract

`make validate` is non-interactive. No prompts, no human input. If you add
a step that requires interaction, gate it behind an explicit flag.
