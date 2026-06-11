#!/usr/bin/env python3
"""Fetch the Rocketlane OpenAPI spec from their hosted docs and diff against the committed copy."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import httpx

DOCS_PAGE = "https://developer.rocketlane.com/reference/create-comment"
REGISTRY_BASE = "https://dash.readme.com/api/v1/api-registry"
SPEC_FILE = Path(__file__).parent.parent / "rocketlane_cli" / "openapi.json"
PATCHES_FILE = Path(__file__).parent / "patches.json"


def _discover_registry_id() -> str:
    """Extract the current registry ID from oasPublicUrl embedded in the ReadMe page HTML.

    ReadMe embeds a JSON config in the page source containing:
      "oasPublicUrl":"@<project>/v<ver>#<registry-id>"
    The fragment after # is the ID passed to the registry API.
    """
    import re
    resp = httpx.get(DOCS_PAGE, timeout=30)
    resp.raise_for_status()
    match = re.search(r'"oasPublicUrl"\s*:\s*"[^"]*#([a-z0-9]+)"', resp.text)
    if not match:
        raise RuntimeError("Could not find oasPublicUrl in developer.rocketlane.com page source")
    return match.group(1)


def fetch_spec() -> dict:
    registry_id = _discover_registry_id()
    print(f"Registry ID: {registry_id}")
    resp = httpx.get(f"{REGISTRY_BASE}/{registry_id}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def apply_patches(spec: dict) -> dict:
    """Deep-merge PATCHES_FILE into spec for endpoints not covered by the official spec."""
    if not PATCHES_FILE.exists():
        return spec

    patches = json.loads(PATCHES_FILE.read_text())
    if not patches:
        return spec

    result = copy.deepcopy(spec)

    # Merge paths
    for path, methods in patches.get("paths", {}).items():
        if path not in result["paths"]:
            result["paths"][path] = methods
            print(f"  ~ patch   added path {path}")
        else:
            for method, operation in methods.items():
                if method not in result["paths"][path]:
                    result["paths"][path][method] = operation
                    print(f"  ~ patch   added {method.upper()} {path}")
                else:
                    # Merge parameters and requestBody into existing operation
                    existing = result["paths"][path][method]
                    for param in operation.get("parameters", []):
                        names = {p["name"] for p in existing.get("parameters", [])}
                        if param["name"] not in names:
                            existing.setdefault("parameters", []).append(param)
                            print(f"  ~ patch   added param {param['name']} to {method.upper()} {path}")
                    if "requestBody" in operation and "requestBody" not in existing:
                        existing["requestBody"] = operation["requestBody"]
                        print(f"  ~ patch   added requestBody to {method.upper()} {path}")

    # Merge component schemas
    patch_schemas = patches.get("components", {}).get("schemas", {})
    if patch_schemas:
        result.setdefault("components", {}).setdefault("schemas", {}).update(patch_schemas)
        print(f"  ~ patch   merged {len(patch_schemas)} component schema(s)")

    return result


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
    print("Fetching spec from dash.readme.com...")
    try:
        new_spec = fetch_spec()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    new_spec = apply_patches(new_spec)

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
