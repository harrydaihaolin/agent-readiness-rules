# Security policy

## Reporting

Email security reports to the maintainers via GitHub Security Advisories
on this repository.

## Scope

This repo contains only YAML rule definitions and metadata. No code is
executed by anything in this repo; consumers (the OSS evaluator and the
closed engine) load and evaluate the rules. Bugs in those evaluators
belong in their respective repos.

A malicious rule could in principle cause a downstream evaluator to read
files it shouldn't (path traversal via glob); the agent-readiness rule
loader is responsible for sandboxing globs to the target repo. Report
such issues against the consumer repo.
