#!/usr/bin/env python3
"""Regenerate `tests/expected/{good,noisy,broken,monorepo}.json` snapshots.

Mirrors the normalisation block in `.github/workflows/ci.yml` so that
local regen matches what CI diffs against. Keep the two in sync.

Layout assumed (sibling-checkout):

    workspace/
      agent-readiness/                (OSS engine source)
      agent-readiness-fixtures/       (the four fixtures live in fixtures/)
      agent-readiness-rules/          (this repo; tests/expected/*.json target)

Usage:

    python3 scripts/regen_snapshots.py
    # or via the Makefile:
    make snapshots
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable

FIXTURES = ("good", "noisy", "broken", "monorepo")


def _project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _resolve(p: str | Path, *, base: Path) -> Path:
    path = Path(p)
    return path if path.is_absolute() else (base / path).resolve()


def _normalise(path: Path, fixture_name: str) -> None:
    """Rewrite absolute paths inside the snapshot to a stable relative form.

    Mirrors the inline Python block in `.github/workflows/ci.yml`. The
    snapshot must diff cleanly across runners with different checkout
    paths; we replace the runner-specific `repo_path` and prefix-strip
    each finding's `file` path.
    """
    with path.open() as fh:
        data = json.load(fh)
    data["repo_path"] = f"fixtures/{fixture_name}"
    for check in data.get("checks", []):
        for finding in check.get("findings") or []:
            if isinstance(finding, dict) and isinstance(finding.get("file"), str):
                key = f"/fixtures/{fixture_name}/"
                idx = finding["file"].find(key)
                if idx >= 0:
                    finding["file"] = finding["file"][idx + len(key):]
    with path.open("w") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
        fh.write("\n")


def _run_eval(
    *,
    fixture_dir: Path,
    rules_dir: Path,
    out_path: Path,
    agent_readiness_src: Path | None,
) -> None:
    env = os.environ.copy()
    cmd: list[str]
    if agent_readiness_src is not None:
        # PYTHONPATH-driven invocation matches AGENTS.md "regenerate locally"
        # block, so the two stay in lockstep.
        env["PYTHONPATH"] = (
            f"{agent_readiness_src}{os.pathsep}{env.get('PYTHONPATH', '')}"
        )
        cmd = [
            sys.executable,
            "-m",
            "agent_readiness.cli",
            "rules-eval",
            str(fixture_dir),
            "--rules",
            str(rules_dir),
            "--json",
        ]
    else:
        cmd = [
            "agent-readiness",
            "rules-eval",
            str(fixture_dir),
            "--rules",
            str(rules_dir),
            "--json",
        ]
    proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stderr)
        raise SystemExit(
            f"agent-readiness rules-eval failed for {fixture_dir} (exit {proc.returncode})"
        )
    out_path.write_text(proc.stdout)


def regen(
    *,
    rules_root: Path,
    fixtures_root: Path,
    agent_readiness_src: Path | None,
    fixtures: Iterable[str] = FIXTURES,
) -> None:
    expected_dir = rules_root / "tests" / "expected"
    expected_dir.mkdir(parents=True, exist_ok=True)
    rules_dir = rules_root / "rules"
    if not rules_dir.is_dir():
        raise SystemExit(f"rules dir not found: {rules_dir}")
    for fix in fixtures:
        fixture_dir = fixtures_root / fix
        if not fixture_dir.is_dir():
            raise SystemExit(
                f"fixture dir not found: {fixture_dir}\n"
                "Pass --fixtures-root to point at the parent of {good,noisy,...}"
            )
        out_path = expected_dir / f"{fix}.json"
        print(f"=== fixture: {fix} ===", flush=True)
        _run_eval(
            fixture_dir=fixture_dir,
            rules_dir=rules_dir,
            out_path=out_path,
            agent_readiness_src=agent_readiness_src,
        )
        _normalise(out_path, fix)
        print(f"wrote {out_path.relative_to(rules_root)}")


def main(argv: list[str] | None = None) -> int:
    rules_root = _project_root()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fixtures-root",
        default=str(rules_root.parent / "agent-readiness-fixtures" / "fixtures"),
        help=(
            "Directory containing {good,noisy,broken,monorepo}/ fixture trees. "
            "Defaults to the sibling-checkout layout described in AGENTS.md."
        ),
    )
    parser.add_argument(
        "--agent-readiness-src",
        default=str(rules_root.parent / "agent-readiness" / "src"),
        help=(
            "Path to a local agent-readiness/src checkout to put on PYTHONPATH. "
            "Pass empty string to use whatever `agent-readiness` is on PATH."
        ),
    )
    parser.add_argument(
        "--fixture",
        action="append",
        choices=FIXTURES,
        help="Regenerate only this fixture (repeatable). Defaults to all four.",
    )
    args = parser.parse_args(argv)

    fixtures_root = _resolve(args.fixtures_root, base=rules_root)
    src_arg = args.agent_readiness_src.strip()
    agent_readiness_src: Path | None
    if src_arg:
        agent_readiness_src = _resolve(src_arg, base=rules_root)
        if not agent_readiness_src.is_dir():
            print(
                f"warning: agent-readiness src not found at {agent_readiness_src}; "
                "falling back to the `agent-readiness` binary on PATH.",
                file=sys.stderr,
            )
            agent_readiness_src = None
    else:
        agent_readiness_src = None
    if agent_readiness_src is None and shutil.which("agent-readiness") is None:
        raise SystemExit(
            "neither --agent-readiness-src nor a global `agent-readiness` "
            "binary is available; install one or pass --agent-readiness-src"
        )

    regen(
        rules_root=rules_root,
        fixtures_root=fixtures_root,
        agent_readiness_src=agent_readiness_src,
        fixtures=tuple(args.fixture) if args.fixture else FIXTURES,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
