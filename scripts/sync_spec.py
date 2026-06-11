#!/usr/bin/env python3
"""Fetch the Rocketlane OpenAPI spec from their hosted docs and diff against the committed copy."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import httpx

SPEC_URL = (
    "https://developer.rocketlane.com"
    "/rocketlanev4/api-next/v2/branches/1.3/reference/get-phase"
)
SPEC_FILE = Path(__file__).parent.parent / "openapi.json"


def fetch_spec() -> dict:
    resp = httpx.get(SPEC_URL, params={"reduce": "false"}, timeout=30)
    resp.raise_for_status()
    return resp.json()["data"]["api"]["schema"]


def diff_paths(old: dict, new: dict) -> bool:
    """Print a diff of paths between old and new specs. Returns True if changed."""
    old_paths = set(old.get("paths", {}).keys())
    new_paths = set(new.get("paths", {}).keys())

    added = new_paths - old_paths
    removed = old_paths - new_paths

    # Check for method-level changes on existing paths
    changed = []
    for path in sorted(old_paths & new_paths):
        old_methods = set(old["paths"][path].keys())
        new_methods = set(new["paths"][path].keys())
        if old_methods != new_methods:
            changed.append((path, old_methods, new_methods))

    if not added and not removed and not changed:
        return False

    if added:
        print("  New paths:")
        for p in sorted(added):
            methods = sorted(new["paths"][p].keys())
            print(f"    + {p}  [{', '.join(methods)}]")
    if removed:
        print("  Removed paths:")
        for p in sorted(removed):
            print(f"    - {p}")
    if changed:
        print("  Changed methods:")
        for path, old_m, new_m in changed:
            for m in sorted(new_m - old_m):
                print(f"    + {path}  [{m}]")
            for m in sorted(old_m - new_m):
                print(f"    - {path}  [{m}]")

    return True


def main() -> int:
    print("Fetching spec from developer.rocketlane.com...")
    try:
        new_spec = fetch_spec()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    path_count = len(new_spec.get("paths", {}))
    schema_count = len(new_spec.get("components", {}).get("schemas", {}))
    print(f"Fetched: {path_count} paths, {schema_count} component schemas")

    if SPEC_FILE.exists():
        old_spec = json.loads(SPEC_FILE.read_text())
        changed = diff_paths(old_spec, new_spec)
        if changed:
            print("\nSpec has changed — updating openapi.json")
        else:
            print("No path changes detected.")
    else:
        print("No existing spec found — writing openapi.json")
        changed = True

    if changed:
        SPEC_FILE.write_text(json.dumps(new_spec, indent=2) + "\n")
        print(f"Wrote {SPEC_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
