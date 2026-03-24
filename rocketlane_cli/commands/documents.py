"""Space document management commands — 5 endpoints."""

import click

from rocketlane_cli.client import RocketlaneClient
from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("documents")
def documents():
    """Manage documents within spaces."""


@documents.command("list")
@click.argument("space_id", type=int)
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_documents(ctx, space_id, limit, offset, as_json):
    """List all documents in a space."""
    client = get_client(ctx)
    data = client.get(f"/spaces/{space_id}/documents", limit=limit, offset=offset)
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, title=f"Documents in Space #{space_id}")


@documents.command("get")
@click.argument("space_id", type=int)
@click.argument("doc_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_document(ctx, space_id, doc_id, as_json):
    """Get a single document."""
    client = get_client(ctx)
    data = client.get(f"/spaces/{space_id}/documents/{doc_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Document #{doc_id}")


@documents.command("create")
@click.argument("space_id", type=int)
@click.option("--title", required=True, help="Document title")
@click.option("--content", help="Document content")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def create_document(ctx, space_id, title, content, as_json):
    """Create a new document in a space."""
    client = get_client(ctx)
    body = {"title": title}
    if content:
        body["content"] = content
    data = client.post(f"/spaces/{space_id}/documents", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title="Document Created")


@documents.command("update")
@click.argument("space_id", type=int)
@click.argument("doc_id", type=int)
@click.option("--title", help="New title")
@click.option("--content", help="New content")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def update_document(ctx, space_id, doc_id, title, content, as_json):
    """Update a document."""
    client = get_client(ctx)
    body = {}
    if title:
        body["title"] = title
    if content:
        body["content"] = content
    if not body:
        click.echo("Nothing to update. Provide at least one option.")
        return
    data = client.put(f"/spaces/{space_id}/documents/{doc_id}", body)
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Document #{doc_id} Updated")


@documents.command("delete")
@click.argument("space_id", type=int)
@click.argument("doc_id", type=int)
@click.confirmation_option(prompt="Are you sure you want to delete this document?")
@click.pass_context
def delete_document(ctx, space_id, doc_id):
    """Delete a document."""
    client = get_client(ctx)
    client.delete(f"/spaces/{space_id}/documents/{doc_id}")
    click.echo(click.style(f"  ✓ Document #{doc_id} deleted.", fg="green"))
