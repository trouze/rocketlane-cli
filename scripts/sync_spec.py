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
SPEC_FILE = Path(__file__).parent.parent / "rocketlane_cli" / "openapi.json"


def fetch_spec() -> dict:
    resp = httpx.get(SPEC_URL, params={"reduce": "false"}, timeout=30)
    resp.raise_for_status()
    return resp.json()["data"]["api"]["schema"]


def _body_props(operation: dict) -> set[str]:
    """Return top-level property names from an operation's JSON request body."""
    try:
        schema = operation["requestBody"]["content"]["application/json"]["schema"]
        if "allOf" in schema:
            props: dict = {}
            for sub in schema["allOf"]:
                props.update(sub.get("properties", {}))
            return set(props)
        return set(schema.get("properties", {}))
    except (KeyError, TypeError):
        return set()


def diff_spec(old: dict, new: dict) -> bool:
    """Print a structured diff of two specs at path/method/param/body level.

    Returns True if anything changed.
    """
    old_paths = old.get("paths", {})
    new_paths = new.get("paths", {})
    changed = False

    # New / removed paths
    for p in sorted(set(new_paths) - set(old_paths)):
        methods = sorted(new_paths[p])
        print(f"  + path    {p}  [{', '.join(m.upper() for m in methods)}]")
        changed = True
    for p in sorted(set(old_paths) - set(new_paths)):
        print(f"  - path    {p}")
        changed = True

    # Shared paths: method and operation-level changes
    for path in sorted(set(old_paths) & set(new_paths)):
        old_ops = old_paths[path]
        new_ops = new_paths[path]

        for m in sorted(set(new_ops) - set(old_ops)):
            print(f"  + method  {m.upper()} {path}")
            changed = True
        for m in sorted(set(old_ops) - set(new_ops)):
            print(f"  - method  {m.upper()} {path}")
            changed = True

        for method in sorted(set(old_ops) & set(new_ops)):
            old_op = old_ops[method]
            new_op = new_ops[method]
            label = f"{method.upper()} {path}"

            # Query / path parameters
            old_params = {p["name"]: p for p in old_op.get("parameters", [])}
            new_params = {p["name"]: p for p in new_op.get("parameters", [])}
            for name in sorted(set(new_params) - set(old_params)):
                p_def = new_params[name]
                loc = p_def.get("in", "query")
                req = "*" if p_def.get("required") else ""
                print(f"  + param   {label}  {name} [{loc}{req}]")
                changed = True
            for name in sorted(set(old_params) - set(new_params)):
                print(f"  - param   {label}  {name}")
                changed = True

            # Request body fields
            old_body = _body_props(old_op)
            new_body = _body_props(new_op)
            for name in sorted(new_body - old_body):
                print(f"  + body    {label}  {name}")
                changed = True
            for name in sorted(old_body - new_body):
                print(f"  - body    {label}  {name}")
                changed = True

    return changed


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
        changed = diff_spec(old_spec, new_spec)
        if changed:
            print("\nSpec has changed — updating rocketlane_cli/openapi.json")
        else:
            print("No changes detected.")
    else:
        print("No existing spec — writing rocketlane_cli/openapi.json")
        changed = True

    if changed:
        SPEC_FILE.write_text(json.dumps(new_spec, indent=2) + "\n")
        print(f"Wrote {SPEC_FILE}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
