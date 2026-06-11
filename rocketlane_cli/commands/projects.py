"""Project management commands — 13 endpoints."""

import click

from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("projects")
def projects():
    """Manage Rocketlane projects."""


# ── List / Get ───────────────────────────────────────────────────────────────

@projects.command("list")
@click.option("--status", help="Filter by status (e.g. 'In progress', 'Completed')")
@click.option("--limit", type=int, help="Max results to return")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_projects(ctx, status, limit, offset, as_json):
    """List all projects."""
    client = get_client(ctx)
    data = client.get("/projects", status=status, limit=limit, offset=offset)
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(
        rows,
        columns=["projectId", "projectName", "status", "customer", "owner", "progressPercentage"],
        title="Projects",
    )


@projects.command("get")
@click.argument("project_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_project(ctx, project_id, as_json):
    """Get a single project by ID."""
    client = get_client(ctx)
    data = client.get(f"/projects/{project_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Project #{project_id}")


# ── Create / Update / Delete ────────────────────────────────────────────────

@projects.command("create")
@click.option("--name", required=True, help="Project name")
@click.option("--customer", required=True, help="Customer company name")
@click.option("--owner", required=True, help="Owner email address")
@click.option("--start-date", help="Start date (YYYY-MM-DD)")
@click.option("--due-date", help="Due date (YYYY-MM-DD)")
@click.option("--visibility", type=click.Choice(["EVERYONE", "MEMBERS_ONLY"]))
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def create_project(ctx, name, customer, owner, start_date, due_date, visibility, as_json):
    """Create a new project."""
    client = get_client(ctx)
    body = {
        "projectName": name,
        "customer": {"companyName": customer},
        "owner": {"emailId": owner},
    }
    if start_date:
        body["startDate"] = start_date
    if due_date:
        body["dueDate"] = due_date
    if visibility:
        body["visibility"] = visibility
    data = client.post("/projects", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title="Project Created")


@projects.command("update")
@click.argument("project_id", type=int)
@click.option("--name", help="New project name")
@click.option("--start-date", help="New start date (YYYY-MM-DD)")
@click.option("--due-date", help="New due date (YYYY-MM-DD)")
@click.option("--status", help="New status")
@click.option("--visibility", type=click.Choice(["EVERYONE", "MEMBERS_ONLY"]))
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def update_project(ctx, project_id, name, start_date, due_date, status, visibility, as_json):
    """Update an existing project."""
    client = get_client(ctx)
    body = {}
    if name:
        body["projectName"] = name
    if start_date:
        body["startDate"] = start_date
    if due_date:
        body["dueDate"] = due_date
    if status:
        body["status"] = status
    if visibility:
        body["visibility"] = visibility
    if not body:
        click.echo("Nothing to update. Provide at least one option.")
        return
    data = client.put(f"/projects/{project_id}", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Project #{project_id} Updated")


@projects.command("delete")
@click.argument("project_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this project?")
@click.pass_context
def delete_project(ctx, project_id):
    """Delete a project."""
    client = get_client(ctx)
    client.delete(f"/projects/{project_id}")
    click.echo(click.style(f"  ✓ Project #{project_id} deleted.", fg="green"))


# ── Archive ──────────────────────────────────────────────────────────────────

@projects.command("archive")
@click.argument("project_id", type=int)
@click.pass_context
def archive_project(ctx, project_id):
    """Archive a project."""
    client = get_client(ctx)
    data = client.post(f"/projects/{project_id}/archive")
    render_detail(data, title=f"Project #{project_id} Archived")


# ── Members ──────────────────────────────────────────────────────────────────

@projects.command("add-members")
@click.argument("project_id", type=int)
@click.option("--emails", required=True, help="Comma-separated email addresses")
@click.pass_context
def add_members(ctx, project_id, emails):
    """Add members to a project."""
    client = get_client(ctx)
    email_list = [e.strip() for e in emails.split(",")]
    body = {"members": [{"emailId": e} for e in email_list]}
    client.post(f"/projects/{project_id}/members", body)
    click.echo(click.style(f"  ✓ Added {len(email_list)} member(s) to project #{project_id}.", fg="green"))


@projects.command("remove-members")
@click.argument("project_id", type=int)
@click.option("--emails", required=True, help="Comma-separated email addresses")
@click.pass_context
def remove_members(ctx, project_id, emails):
    """Remove members from a project."""
    client = get_client(ctx)
    email_list = [e.strip() for e in emails.split(",")]
    body = {"members": [{"emailId": e} for e in email_list]}
    client.post(f"/projects/{project_id}/members/remove", body)
    click.echo(click.style(f"  ✓ Removed {len(email_list)} member(s) from project #{project_id}.", fg="green"))


# ── Template ─────────────────────────────────────────────────────────────────

@projects.command("import-template")
@click.argument("project_id", type=int)
@click.option("--template-id", required=True, type=int, help="Template ID to import")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def import_template(ctx, project_id, template_id, as_json):
    """Import a template into a project."""
    client = get_client(ctx)
    body = {"templateId": template_id}
    data = client.post(f"/projects/{project_id}/template", body)
    if as_json:
        render_json(data)
    else:
        click.echo(click.style(f"  ✓ Template #{template_id} imported into project #{project_id}.", fg="green"))


# ── Placeholders ─────────────────────────────────────────────────────────────

@projects.command("placeholders")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_placeholders(ctx, as_json):
    """Get all project placeholders."""
    client = get_client(ctx)
    data = client.post("/projects/placeholders")
    if as_json:
        render_json(data)
    else:
        rows = data if isinstance(data, list) else data.get("results", data.get("data", []))
        render_table(rows, title="Placeholders")


@projects.command("assign-placeholder")
@click.argument("project_id", type=int)
@click.option("--placeholder-id", required=True, type=int)
@click.option("--user-email", required=True, help="Email of user to assign")
@click.pass_context
def assign_placeholder(ctx, project_id, placeholder_id, user_email):
    """Assign a user to a placeholder."""
    client = get_client(ctx)
    body = {"placeholderId": placeholder_id, "user": {"emailId": user_email}}
    client.post(f"/projects/{project_id}/placeholders", body)
    click.echo(click.style(f"  ✓ Placeholder #{placeholder_id} assigned to {user_email}.", fg="green"))


@projects.command("unassign-placeholder")
@click.argument("project_id", type=int)
@click.option("--placeholder-id", required=True, type=int)
@click.pass_context
def unassign_placeholder(ctx, project_id, placeholder_id):
    """Unassign a placeholder."""
    client = get_client(ctx)
    body = {"placeholderId": placeholder_id}
    client.post(f"/projects/{project_id}/placeholders/unassign", body)
    click.echo(click.style(f"  ✓ Placeholder #{placeholder_id} unassigned.", fg="green"))
