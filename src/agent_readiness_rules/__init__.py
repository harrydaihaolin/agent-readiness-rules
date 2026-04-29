"""agent-readiness-rules: declarative YAML rule pack.

The wheel ships the YAML rule files (under ``rules/``) and the
``manifest.toml`` at the same path consumers expect:

    importlib.resources.files("agent_readiness_rules") / "rules"
    importlib.resources.files("agent_readiness_rules") / "manifest.toml"

The helpers below wrap the importlib.resources dance so consumers don't
have to know about the indirection.
"""

from __future__ import annotations

from importlib.resources import files
from pathlib import Path

__version__ = "2.0.0a0"


def rules_dir() -> Path:
    """Return the path to the bundled rules directory.

    Always points at a real on-disk directory (we don't ship the wheel
    as a zipfile). Raises ``FileNotFoundError`` if the install is
    corrupted and the directory is missing — in practice the worst
    that should happen is the package wasn't installed correctly.
    """
    traversable = files(__name__).joinpath("rules")
    path = Path(str(traversable))
    if not path.is_dir():
        raise FileNotFoundError(
            f"agent_readiness_rules: rules directory missing at {path}; "
            "reinstall agent-readiness-rules to repair."
        )
    return path


def manifest_path() -> Path:
    """Return the path to the bundled manifest.toml."""
    traversable = files(__name__).joinpath("manifest.toml")
    return Path(str(traversable))


def list_rule_files() -> list[Path]:
    """Convenience: every ``*.yaml`` under :func:`rules_dir`, sorted.

    Useful for downstream tooling that wants to walk the pack without
    re-implementing the directory traversal.
    """
    return sorted(rules_dir().rglob("*.yaml"))


__all__ = ["__version__", "rules_dir", "manifest_path", "list_rule_files"]
