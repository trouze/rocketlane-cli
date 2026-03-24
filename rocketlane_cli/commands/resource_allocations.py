"""Resource allocation commands — 1 endpoint."""

import click

from rocketlane_cli.client import RocketlaneClient
from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table


@click.group("allocations")
def resource_allocations():
    """View resource allocations."""


@resource_allocations.command("list")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--user-id", type=int, help="Filter by user ID")
@click.option("--from-date", help="From date (YYYY-MM-DD)")
@click.option("--to-date", help="To date (YYYY-MM-DD)")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_allocations(ctx, project_id, user_id, from_date, to_date, limit, offset, as_json):
    """List all resource allocations."""
    client = get_client(ctx)
    data = client.get(
        "/resource-allocations",
        projectId=project_id,
        userId=user_id,
        fromDate=from_date,
        toDate=to_date,
        limit=limit,
        offset=offset,
    )
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, title="Resource Allocations")
