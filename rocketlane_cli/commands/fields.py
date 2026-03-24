"""Custom field management commands — 7 endpoints."""

import click

from rocketlane_cli.client import RocketlaneClient
from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("fields")
def fields():
    """Manage custom fields."""


@fields.command("list")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_fields(ctx, limit, offset, as_json):
    """List all custom fields."""
    client = get_client(ctx)
    data = client.get("/fields", limit=limit, offset=offset)
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, columns=["fieldId", "fieldLabel", "fieldType", "entityType"], title="Custom Fields")


@fields.command("get")
@click.argument("field_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_field(ctx, field_id, as_json):
    """Get a single field by ID."""
    client = get_client(ctx)
    data = client.get(f"/fields/{field_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Field #{field_id}")


@fields.command("create")
@click.option("--label", required=True, help="Field label")
@click.option("--type", "field_type", required=True, help="Field type (e.g. TEXT, NUMBER, DROPDOWN)")
@click.option("--entity-type", required=True, help="Entity type (e.g. PROJECT, TASK)")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def create_field(ctx, label, field_type, entity_type, as_json):
    """Create a new custom field."""
    client = get_client(ctx)
    body = {"fieldLabel": label, "fieldType": field_type, "entityType": entity_type}
    data = client.post("/fields", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title="Field Created")


@fields.command("update")
@click.argument("field_id", type=int)
@click.option("--label", help="New field label")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def update_field(ctx, field_id, label, as_json):
    """Update a custom field."""
    client = get_client(ctx)
    body = {}
    if label:
        body["fieldLabel"] = label
    if not body:
        click.echo("Nothing to update. Provide at least one option.")
        return
    data = client.put(f"/fields/{field_id}", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Field #{field_id} Updated")


@fields.command("delete")
@click.argument("field_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this field?")
@click.pass_context
def delete_field(ctx, field_id):
    """Delete a custom field."""
    client = get_client(ctx)
    client.delete(f"/fields/{field_id}")
    click.echo(click.style(f"  ✓ Field #{field_id} deleted.", fg="green"))


@fields.command("add-option")
@click.argument("field_id", type=int)
@click.option("--value", required=True, help="Option value")
@click.option("--label", help="Option display label")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def add_option(ctx, field_id, value, label, as_json):
    """Add an option to a dropdown field."""
    client = get_client(ctx)
    body = {"value": value}
    if label:
        body["label"] = label
    data = client.post(f"/fields/{field_id}/options", body)
    if as_json:
        render_json(data)
    else:
        click.echo(click.style(f"  ✓ Option '{value}' added to field #{field_id}.", fg="green"))


@fields.command("update-option")
@click.argument("field_id", type=int)
@click.option("--option-id", required=True, help="Option ID to update")
@click.option("--value", help="New option value")
@click.option("--label", help="New option label")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def update_option(ctx, field_id, option_id, value, label, as_json):
    """Update a field option."""
    client = get_client(ctx)
    body = {"optionId": option_id}
    if value:
        body["value"] = value
    if label:
        body["label"] = label
    data = client.post(f"/fields/{field_id}/options/update", body)
    if as_json:
        render_json(data)
    else:
        click.echo(click.style(f"  ✓ Option updated on field #{field_id}.", fg="green"))
