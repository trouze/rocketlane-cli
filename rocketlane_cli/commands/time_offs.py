"""Time-off management commands — 4 endpoints."""

import click

from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("time-offs")
def time_offs():
    """Manage time-off requests."""


@time_offs.command("list")
@click.option("--user-id", type=int, help="Filter by user ID")
@click.option("--from-date", help="From date (YYYY-MM-DD)")
@click.option("--to-date", help="To date (YYYY-MM-DD)")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_time_offs(ctx, user_id, from_date, to_date, limit, offset, as_json):
    """List all time-offs."""
    client = get_client(ctx)
    data = client.get(
        "/time-offs",
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
    render_table(rows, title="Time-Offs")


@time_offs.command("get")
@click.argument("time_off_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_time_off(ctx, time_off_id, as_json):
    """Get a time-off by ID."""
    client = get_client(ctx)
    data = client.get(f"/time-offs/{time_off_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Time-Off #{time_off_id}")


@time_offs.command("create")
@click.option("--user-id", type=int, help="User ID")
@click.option("--user-email", help="User email")
@click.option("--from-date", required=True, help="Start date (YYYY-MM-DD)")
@click.option("--to-date", required=True, help="End date (YYYY-MM-DD)")
@click.option("--reason", help="Reason for time-off")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def create_time_off(ctx, user_id, user_email, from_date, to_date, reason, as_json):
    """Create a time-off entry."""
    client = get_client(ctx)
    body = {"fromDate": from_date, "toDate": to_date}
    if user_id:
        body["userId"] = user_id
    if user_email:
        body["user"] = {"emailId": user_email}
    if reason:
        body["reason"] = reason
    data = client.post("/time-offs", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title="Time-Off Created")


@time_offs.command("delete")
@click.argument("time_off_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this time-off?")
@click.pass_context
def delete_time_off(ctx, time_off_id):
    """Delete a time-off entry."""
    client = get_client(ctx)
    client.delete(f"/time-offs/{time_off_id}")
    click.echo(click.style(f"  ✓ Time-off #{time_off_id} deleted.", fg="green"))
