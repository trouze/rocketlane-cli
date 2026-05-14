"""Task management commands — 12 endpoints."""

import click

from rocketlane_cli.client import RocketlaneClient
from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("tasks")
def tasks():
    """Manage tasks within projects."""


# ── List / Get ───────────────────────────────────────────────────────────────

@tasks.command("list")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--status", help="Filter by status")
@click.option("--assignee", help="Filter by assignee email")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_tasks(ctx, project_id, status, assignee, limit, offset, as_json):
    """List all tasks."""
    client = get_client(ctx)
    data = client.get(
        "/tasks",
        projectId=project_id,
        status=status,
        assignee=assignee,
        limit=limit,
        offset=offset,
    )
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(
        rows,
        columns=["taskId", "taskName", "status", "startDate", "dueDate", "assignees"],
        title="Tasks",
    )


@tasks.command("get")
@click.argument("task_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_task(ctx, task_id, as_json):
    """Get a single task by ID."""
    client = get_client(ctx)
    data = client.get(f"/tasks/{task_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Task #{task_id}")


# ── Create / Update / Delete ────────────────────────────────────────────────

@tasks.command("create")
@click.option("--project-id", required=True, type=int, help="Parent project ID")
@click.option("--name", required=True, help="Task name")
@click.option("--start-date", help="Start date (YYYY-MM-DD)")
@click.option("--due-date", help="Due date (YYYY-MM-DD)")
@click.option("--effort", type=float, help="Effort in hours")
@click.option("--phase-id", type=int, help="Phase ID to assign task to")
@click.option("--description", help="Task description")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def create_task(ctx, project_id, name, start_date, due_date, effort, phase_id, description, as_json):
    """Create a new task."""
    client = get_client(ctx)
    body = {"project": {"projectId": project_id}, "taskName": name}
    if start_date:
        body["startDate"] = start_date
    if due_date:
        body["dueDate"] = due_date
    if effort is not None:
        body["effort"] = effort
    if phase_id:
        body["phase"] = {"phaseId": phase_id}
    if description:
        body["description"] = description
    data = client.post("/tasks", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title="Task Created")


@tasks.command("update")
@click.argument("task_id", type=int)
@click.option("--name", help="New task name")
@click.option("--start-date", help="New start date (YYYY-MM-DD)")
@click.option("--due-date", help="New due date (YYYY-MM-DD)")
@click.option("--effort", type=float, help="Effort in hours")
@click.option("--status", help="New status")
@click.option("--description", help="New description")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def update_task(ctx, task_id, name, start_date, due_date, effort, status, description, as_json):
    """Update an existing task."""
    client = get_client(ctx)
    body = {}
    if name:
        body["taskName"] = name
    if start_date:
        body["startDate"] = start_date
    if due_date:
        body["dueDate"] = due_date
    if effort is not None:
        body["effort"] = effort
    if status:
        body["status"] = status
    if description:
        body["description"] = description
    if not body:
        click.echo("Nothing to update. Provide at least one option.")
        return
    data = client.put(f"/tasks/{task_id}", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Task #{task_id} Updated")


@tasks.command("delete")
@click.argument("task_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this task?")
@click.pass_context
def delete_task(ctx, task_id):
    """Delete a task."""
    client = get_client(ctx)
    client.delete(f"/tasks/{task_id}")
    click.echo(click.style(f"  ✓ Task #{task_id} deleted.", fg="green"))


# ── Assignees ────────────────────────────────────────────────────────────────

@tasks.command("assign")
@click.argument("task_id", type=int)
@click.option("--emails", required=True, help="Comma-separated assignee emails")
@click.pass_context
def add_assignees(ctx, task_id, emails):
    """Add assignees to a task."""
    client = get_client(ctx)
    email_list = [e.strip() for e in emails.split(",")]
    body = {"assignees": [{"emailId": e} for e in email_list]}
    client.post(f"/tasks/{task_id}/assignees", body)
    click.echo(click.style(f"  ✓ Assigned {len(email_list)} user(s) to task #{task_id}.", fg="green"))


@tasks.command("unassign")
@click.argument("task_id", type=int)
@click.option("--emails", required=True, help="Comma-separated assignee emails")
@click.pass_context
def remove_assignees(ctx, task_id, emails):
    """Remove assignees from a task."""
    client = get_client(ctx)
    email_list = [e.strip() for e in emails.split(",")]
    body = {"assignees": [{"emailId": e} for e in email_list]}
    client.post(f"/tasks/{task_id}/assignees/remove", body)
    click.echo(click.style(f"  ✓ Removed {len(email_list)} assignee(s) from task #{task_id}.", fg="green"))


# ── Followers ────────────────────────────────────────────────────────────────

@tasks.command("add-followers")
@click.argument("task_id", type=int)
@click.option("--emails", required=True, help="Comma-separated follower emails")
@click.pass_context
def add_followers(ctx, task_id, emails):
    """Add followers to a task."""
    client = get_client(ctx)
    email_list = [e.strip() for e in emails.split(",")]
    body = {"followers": [{"emailId": e} for e in email_list]}
    client.post(f"/tasks/{task_id}/followers", body)
    click.echo(click.style(f"  ✓ Added {len(email_list)} follower(s) to task #{task_id}.", fg="green"))


@tasks.command("remove-followers")
@click.argument("task_id", type=int)
@click.option("--emails", required=True, help="Comma-separated follower emails")
@click.pass_context
def remove_followers(ctx, task_id, emails):
    """Remove followers from a task."""
    client = get_client(ctx)
    email_list = [e.strip() for e in emails.split(",")]
    body = {"followers": [{"emailId": e} for e in email_list]}
    client.post(f"/tasks/{task_id}/followers/remove", body)
    click.echo(click.style(f"  ✓ Removed {len(email_list)} follower(s) from task #{task_id}.", fg="green"))


# ── Dependencies ─────────────────────────────────────────────────────────────

@tasks.command("add-deps")
@click.argument("task_id", type=int)
@click.option("--dep-ids", required=True, help="Comma-separated dependency task IDs")
@click.pass_context
def add_dependencies(ctx, task_id, dep_ids):
    """Add dependencies to a task."""
    client = get_client(ctx)
    ids = [int(i.strip()) for i in dep_ids.split(",")]
    body = {"dependencies": [{"taskId": i} for i in ids]}
    client.post(f"/tasks/{task_id}/dependencies", body)
    click.echo(click.style(f"  ✓ Added {len(ids)} dependency(ies) to task #{task_id}.", fg="green"))


@tasks.command("remove-deps")
@click.argument("task_id", type=int)
@click.option("--dep-ids", required=True, help="Comma-separated dependency task IDs")
@click.pass_context
def remove_dependencies(ctx, task_id, dep_ids):
    """Remove dependencies from a task."""
    client = get_client(ctx)
    ids = [int(i.strip()) for i in dep_ids.split(",")]
    body = {"dependencies": [{"taskId": i} for i in ids]}
    client.post(f"/tasks/{task_id}/dependencies/remove", body)
    click.echo(click.style(f"  ✓ Removed {len(ids)} dependency(ies) from task #{task_id}.", fg="green"))


# ── Move to Phase ────────────────────────────────────────────────────────────

@tasks.command("move-to-phase")
@click.argument("task_id", type=int)
@click.option("--phase-id", required=True, type=int, help="Target phase ID")
@click.pass_context
def move_to_phase(ctx, task_id, phase_id):
    """Move a task to a different phase."""
    client = get_client(ctx)
    body = {"phaseId": phase_id}
    client.post(f"/tasks/{task_id}/phase", body)
    click.echo(click.style(f"  ✓ Task #{task_id} moved to phase #{phase_id}.", fg="green"))
