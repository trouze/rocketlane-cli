"""User commands — 2 endpoints."""

import click

from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("users")
def users():
    """View Rocketlane users."""


@users.command("list")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_users(ctx, limit, offset, as_json):
    """List all users."""
    client = get_client(ctx)
    data = client.get("/users", limit=limit, offset=offset)
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, columns=["userId", "firstName", "lastName", "emailId", "role"], title="Users")


@users.command("get")
@click.argument("user_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_user(ctx, user_id, as_json):
    """Get a single user by ID."""
    client = get_client(ctx)
    data = client.get(f"/users/{user_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"User #{user_id}")
