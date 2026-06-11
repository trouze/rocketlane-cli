"""Invoice commands — 4 endpoints."""

import click

from rocketlane_cli.cli_utils import get_client
from rocketlane_cli.ui.output import render_json, render_table, render_detail


@click.group("invoices")
def invoices():
    """View invoices and payments."""


@invoices.command("list")
@click.option("--project-id", type=int, help="Filter by project ID")
@click.option("--status", help="Filter by invoice status")
@click.option("--limit", type=int, help="Max results")
@click.option("--offset", type=int, help="Pagination offset")
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def list_invoices(ctx, project_id, status, limit, offset, as_json):
    """List all invoices."""
    client = get_client(ctx)
    data = client.get("/invoices", projectId=project_id, status=status, limit=limit, offset=offset)
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, title="Invoices")


@invoices.command("get")
@click.argument("invoice_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_invoice(ctx, invoice_id, as_json):
    """Get a single invoice."""
    client = get_client(ctx)
    data = client.get(f"/invoices/{invoice_id}")
    if as_json:
        render_json(data)
    else:
        render_detail(data, title=f"Invoice #{invoice_id}")


@invoices.command("payments")
@click.argument("invoice_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_payments(ctx, invoice_id, as_json):
    """Get payments for an invoice."""
    client = get_client(ctx)
    data = client.get(f"/invoices/{invoice_id}/payments")
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, title=f"Payments for Invoice #{invoice_id}")


@invoices.command("line-items")
@click.argument("invoice_id", type=int)
@click.option("--json", "as_json", is_flag=True, help="Output raw JSON")
@click.pass_context
def get_line_items(ctx, invoice_id, as_json):
    """Get line items for an invoice."""
    client = get_client(ctx)
    data = client.get(f"/invoices/{invoice_id}/line-items")
    if as_json:
        render_json(data)
        return
    rows = data if isinstance(data, list) else data.get("results", data.get("data", [data]))
    render_table(rows, title=f"Line Items for Invoice #{invoice_id}")
