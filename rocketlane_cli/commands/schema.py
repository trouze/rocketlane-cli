"""Schema command — exposes the bundled OpenAPI spec for agent and tool use."""

from __future__ import annotations

import json
from importlib.resources import files

import click


def _load_spec() -> dict:
    text = files("rocketlane_cli").joinpath("openapi.json").read_text(encoding="utf-8")
    return json.loads(text)


@click.command("schema")
@click.option("--path", "path_filter", help="Filter to paths containing this substring (e.g. /tasks)")
@click.option("--method", help="Filter to a specific HTTP method (get, post, put, delete)")
def schema(path_filter, method):
    """Output the Rocketlane API schema as JSON.

    Useful for agents to inspect available endpoints, parameters, and request/response shapes
    before calling `rocketlane api`.

    \b
    Examples:
      rocketlane schema
      rocketlane schema --path /tasks
      rocketlane schema --path /tasks --method post
    """
    spec = _load_spec()

    if path_filter or method:
        filtered: dict = {}
        for p, ops in spec.get("paths", {}).items():
            if path_filter and path_filter.lower() not in p.lower():
                continue
            if method:
                m = method.lower()
                if m in ops:
                    filtered[p] = {m: ops[m]}
            else:
                filtered[p] = ops
        output = {**spec, "paths": filtered}
    else:
        output = spec

    click.echo(json.dumps(output, indent=2))
