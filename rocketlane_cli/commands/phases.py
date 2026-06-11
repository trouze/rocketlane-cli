"""Phase management commands — 5 endpoints."""

import click

from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("phases")
def phases():
    """Manage project phases."""


@phases.command("list")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_phases(ctx, project_id, limit, offset, as_json):
    """List all phases."""
    client = get_client(ctx)
    data = client.get("/phases", projectId=project_id, limit=limit, offset=offset)
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, columns=["phaseId", "phaseName", "startDate", "dueDate", "status"], title="Phases")


@phases.command("get")
@click.argument("phase_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_phase(ctx, phase_id, as_json):
    """Get a single phase by ID."""
    client = get_client(ctx)
    data = client.get(f"/phases/{phase_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Phase #{phase_id}")


@phases.command("create")
@click.option("--project-id", required=True, type=int, help="Parent project ID")
@click.option("--name", required=True, help="Phase name")
@click.option("--start-date", help="Start date (YYYY-MM-DD)")
@click.option("--due-date", help="Due date (YYYY-MM-DD)")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def create_phase(ctx, project_id, name, start_date, due_date, as_json):
    """Create a new phase."""
    client = get_client(ctx)
    body = {"project": {"projectId": project_id}, "phaseName": name}
    if start_date:
        body["startDate"] = start_date
    if due_date:
        body["dueDate"] = due_date
    data = client.post("/phases", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title="Phase Created")


@phases.command("update")
@click.argument("phase_id", type=int)
@click.option("--name", help="New phase name")
@click.option("--start-date", help="New start date (YYYY-MM-DD)")
@click.option("--due-date", help="New due date (YYYY-MM-DD)")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def update_phase(ctx, phase_id, name, start_date, due_date, as_json):
    """Update an existing phase."""
    client = get_client(ctx)
    body = {}
    if name:
        body["phaseName"] = name
    if start_date:
        body["startDate"] = start_date
    if due_date:
        body["dueDate"] = due_date
    if not body:
        click.echo("Nothing to update. Provide at least one option.")
        return
    data = client.put(f"/phases/{phase_id}", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Phase #{phase_id} Updated")


@phases.command("delete")
@click.argument("phase_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this phase?")
@click.pass_context
def delete_phase(ctx, phase_id):
    """Delete a phase."""
    client = get_client(ctx)
    client.delete(f"/phases/{phase_id}")
    click.echo(click.style(f"  ✓ Phase #{phase_id} deleted.", fg="green"))
