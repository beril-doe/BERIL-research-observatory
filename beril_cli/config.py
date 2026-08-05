"""User configuration for BERIL CLI (~/.config/beril/config.toml)."""

from __future__ import annotations

import os
import tomllib
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".config" / "beril"
CONFIG_PATH = CONFIG_DIR / "config.toml"

DEFAULT_BASE_URL = "https://beril.kbase.us"


def load() -> dict[str, Any]:
    """Load user config. Returns empty dict if file doesn't exist."""
    if not CONFIG_PATH.exists():
        return {}
    with CONFIG_PATH.open("rb") as f:
        return tomllib.load(f)


def _toml_escape(val: str) -> str:
    """Escape a string for use inside a TOML double-quoted value."""
    return val.replace("\\", "\\\\").replace('"', '\\"')


def save(cfg: dict[str, Any]) -> None:
    """Write config to disk. Only supports the expected section shape."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []

    if "user" in cfg:
        lines.append("[user]")
        for key in ("name", "affiliation", "orcid"):
            val = cfg["user"].get(key, "")
            if val:
                lines.append(f'{key} = "{_toml_escape(val)}"')
        lines.append("")

    if "defaults" in cfg:
        lines.append("[defaults]")
        for key in ("agent",):
            val = cfg["defaults"].get(key, "")
            if val:
                lines.append(f'{key} = "{_toml_escape(val)}"')
        lines.append("")

    if "vertex" in cfg:
        lines.append("[vertex]")
        v = cfg["vertex"]
        lines.append(f'enabled = {"true" if v.get("enabled") else "false"}')
        for key in ("project_id", "region", "credentials_file"):
            val = v.get(key, "")
            if val:
                lines.append(f'{key} = "{_toml_escape(val)}"')
        lines.append("")

    if "beril" in cfg:
        lines.append("[beril]")
        for key in ("base_url",):
            val = cfg["beril"].get(key, "")
            if val:
                lines.append(f'{key} = "{_toml_escape(val)}"')
        lines.append("")

    CONFIG_PATH.write_text("\n".join(lines) + "\n")


def get_default_agent() -> str:
    """Return the user's default agent, or 'claude' as fallback."""
    cfg = load()
    return cfg.get("defaults", {}).get("agent", "claude")


def get_vertex_config() -> dict[str, Any]:
    """Return the [vertex] section, or empty dict if not configured."""
    cfg = load()
    return cfg.get("vertex", {})


def get_base_url() -> str:
    """Return the BERIL server base URL.

    Resolution order:
      1. BERIL_BASE_URL env var (per-invocation override).
      2. [beril].base_url in config.toml (persisted preference).
      3. DEFAULT_BASE_URL compiled in above.

    Trailing slashes are stripped so callers can safely concatenate a
    path like "/api/user/whoami".
    """
    url = os.environ.get("BERIL_BASE_URL") or ""
    if not url:
        cfg = load()
        url = cfg.get("beril", {}).get("base_url") or ""
    if not url:
        url = DEFAULT_BASE_URL
    return url.rstrip("/")


def set_base_url(base_url: str) -> None:
    """Persist ``base_url`` under [beril] in config.toml, preserving other
    sections. Trailing slashes are stripped for consistency with
    :func:`get_base_url`."""
    cfg = load()
    cfg.setdefault("beril", {})["base_url"] = base_url.rstrip("/")
    save(cfg)
