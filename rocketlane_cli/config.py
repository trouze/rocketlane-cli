"""Configuration management for Rocketlane CLI — multi-instance support.

Config file (~/.rocketlane/config.json) schema:
{
    "active": "acme",           # short name of current instance
    "instances": {
        "acme": {
            "api_key": "rl-...",
            "url": "acme.rocketlane.com",
            "name": "acme"
        },
        "globex": { ... }
    }
}
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any


CONFIG_DIR = Path.home() / ".rocketlane"
CONFIG_FILE = CONFIG_DIR / "config.json"

BASE_URL = "https://api.rocketlane.com/api/1.0"


# ── Config file I/O ─────────────────────────────────────────────────────────

def _load_config() -> dict[str, Any]:
    """Load config from disk, returning empty structure if missing."""
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except json.JSONDecodeError:
            pass
    return {}


def _save_config(data: dict[str, Any]) -> None:
    """Write config to disk with restricted permissions."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(data, indent=2))
    CONFIG_FILE.chmod(0o600)


def _ensure_migrated(cfg: dict[str, Any]) -> dict[str, Any]:
    """Migrate legacy single-key config to multi-instance format."""
    if "instances" in cfg:
        return cfg

    # Legacy format: {"api_key": "rl-..."}
    old_key = cfg.get("api_key")
    if not old_key:
        return {"instances": {}, "active": None}

    name = "default"
    new_cfg = {
        "active": name,
        "instances": {
            name: {
                "api_key": old_key,
                "url": "",
                "name": name,
            }
        },
    }
    _save_config(new_cfg)
    return new_cfg


# ── Instance management ─────────────────────────────────────────────────────

def get_instances() -> dict[str, dict[str, str]]:
    """Return all registered instances."""
    cfg = _ensure_migrated(_load_config())
    return cfg.get("instances", {})


def get_active_instance_name() -> str | None:
    """Return the short name of the active instance."""
    cfg = _ensure_migrated(_load_config())
    return cfg.get("active")


def get_active_instance() -> dict[str, str] | None:
    """Return the active instance dict, or None."""
    cfg = _ensure_migrated(_load_config())
    active = cfg.get("active")
    if active:
        return cfg.get("instances", {}).get(active)
    return None


def add_instance(name: str, api_key: str, url: str) -> None:
    """Register a new instance and set it as active."""
    cfg = _ensure_migrated(_load_config())
    instances = cfg.setdefault("instances", {})
    instances[name] = {"api_key": api_key, "url": url, "name": name}
    cfg["active"] = name
    _save_config(cfg)


def switch_instance(name: str) -> dict[str, str]:
    """Switch active instance. Returns the instance dict. Raises if not found."""
    cfg = _ensure_migrated(_load_config())
    instances = cfg.get("instances", {})
    if name not in instances:
        raise KeyError(f"Instance '{name}' not found.")
    cfg["active"] = name
    _save_config(cfg)
    return instances[name]


def remove_instance(name: str) -> None:
    """Remove an instance from config."""
    cfg = _ensure_migrated(_load_config())
    instances = cfg.get("instances", {})
    if name not in instances:
        raise KeyError(f"Instance '{name}' not found.")
    del instances[name]
    if cfg.get("active") == name:
        cfg["active"] = next(iter(instances), None)
    _save_config(cfg)


def short_name_from_url(url: str) -> str:
    """Extract short reference name from instance URL.

    'acme.rocketlane.com' -> 'acme'
    'https://acme.rocketlane.com' -> 'acme'
    """
    url = url.strip().lower()
    url = url.replace("https://", "").replace("http://", "")
    url = url.rstrip("/")
    # acme.rocketlane.com -> acme
    if ".rocketlane.com" in url:
        return url.split(".rocketlane.com")[0].split(".")[-1]
    # fallback: use the full hostname minus TLD
    return url.split(".")[0]


# ── API key resolution ───────────────────────────────────────────────────────

def get_api_key() -> str:
    """Resolve API key: env var > active instance > .env file."""
    # 1. Environment variable override
    key = os.environ.get("ROCKETLANE_API_KEY")
    if key:
        return key

    # 2. Active instance from config
    instance = get_active_instance()
    if instance and instance.get("api_key"):
        return instance["api_key"]

    # 3. .env fallback in current directory
    for env_name in ("rocketlane.env", ".env"):
        env_path = Path.cwd() / env_name
        if env_path.exists():
            content = env_path.read_text().strip()
            if "=" in content:
                for line in content.splitlines():
                    line = line.strip()
                    if line.startswith("ROCKETLANE_API_KEY="):
                        return line.split("=", 1)[1].strip().strip("'\"")
            elif content.startswith("rl-"):
                return content

    # No key found — return None to trigger first-run setup
    return None


# ── Legacy compat ────────────────────────────────────────────────────────────

def save_config(api_key: str) -> None:
    """Legacy save — adds as 'default' instance."""
    add_instance("default", api_key, "")
