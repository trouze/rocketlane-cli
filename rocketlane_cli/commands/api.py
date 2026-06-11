"""Raw API passthrough — lets agents call any endpoint using the spec directly."""

from __future__ import annotations

import json
import re

import click

from rocketlane_cli.cli_utils import get_client


@click.command("api")
@click.argument("method")
@click.argument("path")
@click.option("--param", "-p", "params", multiple=True, metavar="KEY=VALUE",
              help="Path or query param. {key} placeholders in PATH are substituted first; remainder become query params.")
@click.option("--body", "-b", help="JSON request body as a string.")
@click.pass_context
def api(ctx, method, path, params, body):
    """Make a raw authenticated API call and return JSON.

    PATH supports OpenAPI-style placeholders — supply values with --param:

    \b
    Examples:
      rocketlane api GET /tasks --param projectId=123
      rocketlane api GET /phases/{phaseId} --param phaseId=456
      rocketlane api POST /tasks --body '{"name": "My Task", "project": {"projectId": 1}}'
      rocketlane api DELETE /tasks/{taskId} --param taskId=789
    """
    client = get_client(ctx)

    # Strip /1.0 prefix — the client base URL already includes it
    norm_path = re.sub(r"^/1\.0(?=/|$)", "", path)

    # Split params into path substitutions vs query params
    path_keys = set(re.findall(r"\{(\w+)\}", norm_path))
    query_params: dict[str, str] = {}

    for kv in params:
        if "=" not in kv:
            raise click.UsageError(f"--param must be KEY=VALUE, got: {kv!r}")
        k, v = kv.split("=", 1)
        if k in path_keys:
            norm_path = norm_path.replace(f"{{{k}}}", v)
        else:
            query_params[k] = v

    unresolved = re.findall(r"\{(\w+)\}", norm_path)
    if unresolved:
        raise click.UsageError(
            f"Unresolved path param(s): {unresolved}. Supply with --param {unresolved[0]}=<value>"
        )

    json_body: dict | None = None
    if body:
        try:
            json_body = json.loads(body)
        except json.JSONDecodeError as e:
            raise click.UsageError(f"Invalid JSON body: {e}")

    m = method.upper()
    if m == "GET":
        result = client.get(norm_path, **query_params)
    elif m == "POST":
        result = client.post(norm_path, json_body)
    elif m == "PUT":
        result = client.put(norm_path, json_body)
    elif m == "DELETE":
        result = client.delete(norm_path)
    else:
        raise click.UsageError(f"Unsupported method: {method!r}. Use GET, POST, PUT, or DELETE.")

    click.echo(json.dumps(result, indent=2, default=str))
