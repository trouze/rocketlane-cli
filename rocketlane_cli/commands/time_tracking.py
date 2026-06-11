"""Time tracking commands — 7 endpoints."""

import click

from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("time")
def time_tracking():
    """Manage time entries and tracking."""


@time_tracking.command("list")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--user-id", type=int, help="Filter by user ID")
@click.option("--from-date", help="From date (YYYY-MM-DD)")
@click.option("--to-date", help="To date (YYYY-MM-DD)")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_entries(ctx, project_id, user_id, from_date, to_date, limit, offset, as_json):
    """List time entries."""
    client = get_client(ctx)
    data = client.get(
        "/time-entries",
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
    render_table(
        rows,
        columns=["timeEntryId", "date", "hours", "taskName", "projectName", "category", "user"],
        title="Time Entries",
    )


@time_tracking.command("get")
@click.argument("entry_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_entry(ctx, entry_id, as_json):
    """Get a single time entry."""
    client = get_client(ctx)
    data = client.get(f"/time-entries/{entry_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Time Entry #{entry_id}")


@time_tracking.command("create")
@click.option("--task-id", type=int, help="Task ID")
@click.option("--project-id", type=int, help="Project ID")
@click.option("--hours", required=True, type=float, help="Hours worked")
@click.option("--date", required=True, help="Date (YYYY-MM-DD)")
@click.option("--description", help="Description of work")
@click.option("--category", help="Time entry category")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def create_entry(ctx, task_id, project_id, hours, date, description, category, as_json):
    """Log a time entry."""
    client = get_client(ctx)
    body = {"hours": hours, "date": date}
    if task_id:
        body["taskId"] = task_id
    if project_id:
        body["projectId"] = project_id
    if description:
        body["description"] = description
    if category:
        body["category"] = category
    data = client.post("/time-entries", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title="Time Entry Created")


@time_tracking.command("update")
@click.argument("entry_id", type=int)
@click.option("--hours", type=float, help="New hours")
@click.option("--date", help="New date (YYYY-MM-DD)")
@click.option("--description", help="New description")
@click.option("--category", help="New category")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def update_entry(ctx, entry_id, hours, date, description, category, as_json):
    """Update a time entry."""
    client = get_client(ctx)
    body = {}
    if hours is not None:
        body["hours"] = hours
    if date:
        body["date"] = date
    if description:
        body["description"] = description
    if category:
        body["category"] = category
    if not body:
        click.echo("Nothing to update. Provide at least one option.")
        return
    data = client.put(f"/time-entries/{entry_id}", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Time Entry #{entry_id} Updated")


@time_tracking.command("delete")
@click.argument("entry_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this time entry?")
@click.pass_context
def delete_entry(ctx, entry_id):
    """Delete a time entry."""
    client = get_client(ctx)
    client.delete(f"/time-entries/{entry_id}")
    click.echo(click.style(f"  ✓ Time entry #{entry_id} deleted.", fg="green"))


@time_tracking.command("categories")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_categories(ctx, as_json):
    """List time entry categories."""
    client = get_client(ctx)
    data = client.get("/time-entries/categories")
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, title="Time Entry Categories")


@time_tracking.command("search")
@click.option("--query", help="Search query")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--user-id", type=int, help="Filter by user ID")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def search_entries(ctx, query, project_id, user_id, as_json):
    """Search time entries."""
    client = get_client(ctx)
    data = client.get("/time-entries/search", query=query, projectId=project_id, userId=user_id)
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, title="Search Results")
