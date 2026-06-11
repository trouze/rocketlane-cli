"""Space management commands — 6 endpoints."""

import click

from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("spaces")
def spaces():
    """Manage Rocketlane spaces."""


@spaces.command("list")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_spaces(ctx, limit, offset, as_json):
    """List all spaces."""
    client = get_client(ctx)
    data = client.get("/spaces", limit=limit, offset=offset)
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, columns=["spaceId", "spaceName", "description"], title="Spaces")


@spaces.command("get")
@click.argument("space_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_space(ctx, space_id, as_json):
    """Get a single space by ID."""
    client = get_client(ctx)
    data = client.get(f"/spaces/{space_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Space #{space_id}")


@spaces.command("create")
@click.option("--name", required=True, help="Space name")
@click.option("--description", help="Space description")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def create_space(ctx, name, description, as_json):
    """Create a new space."""
    client = get_client(ctx)
    body = {"spaceName": name}
    if description:
        body["description"] = description
    data = client.post("/spaces", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title="Space Created")


@spaces.command("update")
@click.argument("space_id", type=int)
@click.option("--name", help="New space name")
@click.option("--description", help="New description")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def update_space(ctx, space_id, name, description, as_json):
    """Update a space."""
    client = get_client(ctx)
    body = {}
    if name:
        body["spaceName"] = name
    if description:
        body["description"] = description
    if not body:
        click.echo("Nothing to update. Provide at least one option.")
        return
    data = client.put(f"/spaces/{space_id}", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Space #{space_id} Updated")


@spaces.command("delete")
@click.argument("space_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this space?")
@click.pass_context
def delete_space(ctx, space_id):
    """Delete a space."""
    client = get_client(ctx)
    client.delete(f"/spaces/{space_id}")
    click.echo(click.style(f"  ✓ Space #{space_id} deleted.", fg="green"))
