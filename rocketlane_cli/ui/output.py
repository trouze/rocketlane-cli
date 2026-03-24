"""Output formatting — tables, JSON, and styled results."""

from __future__ import annotations

import json
from typing import Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich import box

console = Console()

RL_BLUE = "#3D5AFE"
RL_ACCENT = "#7C8AFF"
RL_DIM = "#4A5568"


def render_json(data: Any) -> None:
    """Pretty-print JSON with syntax highlighting."""
    raw = json.dumps(data, indent=2, default=str)
    syntax = Syntax(raw, "json", theme="monokai", line_numbers=False)
    console.print(syntax)


def render_table(
    rows: list[dict[str, Any]],
    columns: list[str] | None = None,
    title: str | None = None,
) -> None:
    """Render a list of dicts as a rich table."""
    if not rows:
        console.print(f"  [{RL_DIM}]No results.[/]")
        return

    if columns is None:
        columns = list(rows[0].keys())

    table = Table(
        title=title,
        box=box.ROUNDED,
        border_style=RL_DIM,
        header_style=f"bold {RL_ACCENT}",
        title_style=f"bold {RL_BLUE}",
        row_styles=["", f"dim"],
        pad_edge=True,
        expand=False,
    )

    for col in columns:
        table.add_column(col, overflow="fold")

    for row in rows:
        table.add_row(*[_format_cell(row.get(c, "")) for c in columns])

    console.print(table)


def render_detail(data: dict[str, Any], title: str | None = None) -> None:
    """Render a single record as a styled key-value panel."""
    lines = []
    for k, v in data.items():
        if isinstance(v, (dict, list)):
            v = json.dumps(v, indent=2, default=str)
        lines.append(f"[bold {RL_ACCENT}]{k}:[/] {v}")

    panel = Panel(
        "\n".join(lines),
        title=title,
        border_style=RL_DIM,
        title_align="left",
        padding=(1, 2),
    )
    console.print(panel)


def _format_cell(value: Any) -> str:
    """Format a cell value for table display."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "✓" if value else "✗"
    if isinstance(value, dict):
        # Show a compact summary for nested objects
        if "emailId" in value:
            return str(value["emailId"])
        if "companyName" in value:
            return str(value["companyName"])
        if "label" in value:
            return str(value["label"])
        return json.dumps(value, default=str)
    if isinstance(value, list):
        return f"[{len(value)} items]"
    return str(value)
