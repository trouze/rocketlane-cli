"""Main CLI entry point — assembles all command groups."""

import click
from rich.prompt import Prompt
from rich.table import Table
from rich import box

from rocketlane_cli.client import RocketlaneClient, RocketlaneAPIError
from rocketlane_cli.config import (
    get_api_key,
    get_instances,
    get_active_instance,
    get_active_instance_name,
    add_instance,
    switch_instance,
    remove_instance,
    short_name_from_url,
)
from rocketlane_cli.ui.banner import (
    print_banner,
    print_status,
    console,
    RL_BLUE,
    RL_ACCENT,
    RL_DIM,
    RL_GRAY,
)

from rocketlane_cli.commands.projects import projects
from rocketlane_cli.commands.tasks import tasks
from rocketlane_cli.commands.phases import phases
from rocketlane_cli.commands.fields import fields
from rocketlane_cli.commands.users import users
from rocketlane_cli.commands.spaces import spaces
from rocketlane_cli.commands.documents import documents
from rocketlane_cli.commands.time_tracking import time_tracking
from rocketlane_cli.commands.time_offs import time_offs
from rocketlane_cli.commands.resource_allocations import resource_allocations
from rocketlane_cli.commands.invoices import invoices
from rocketlane_cli.commands.schema import schema
from rocketlane_cli.commands.api import api


# ── First-run setup ─────────────────────────────────────────────────────────

def _first_run_setup() -> None:
    """Interactive first-run: prompt for API key + instance URL."""
    print_banner()
    console.print()
    console.print(f"  [{RL_ACCENT}]Welcome to Rocketlane CLI![/]")
    console.print(f"  [{RL_GRAY}]Let's connect your first Rocketlane instance.[/]")
    console.print()

    _prompt_add_instance()


def _prompt_add_instance() -> None:
    """Shared prompt flow for adding an instance."""
    # 1. Instance URL
    console.print(f"  [{RL_GRAY}]Enter your Rocketlane instance URL[/]")
    console.print(f"  [{RL_DIM}]Example: acme.rocketlane.com[/]")
    url = Prompt.ask(f"  [{RL_ACCENT}]Instance URL[/]")
    url = url.strip()

    # Derive short name
    name = short_name_from_url(url)
    console.print(f"  [{RL_DIM}]Short name: [bold]{name}[/bold][/]")
    console.print()

    # 2. API key
    console.print(f"  [{RL_GRAY}]Enter your API key[/]")
    console.print(f"  [{RL_DIM}]Settings > API > Create API key in Rocketlane[/]")
    api_key = Prompt.ask(f"  [{RL_ACCENT}]API Key[/]", password=True)
    api_key = api_key.strip()
    console.print()

    # 3. Validate the key works
    console.print(f"  [{RL_GRAY}]Validating...[/]", end="")
    try:
        client = RocketlaneClient(api_key=api_key)
        client.get("/users", limit=1)
    except Exception:
        console.print()
        print_status("Invalid API key or connection failed. Please try again.", style="error")
        raise SystemExit(1)

    # 4. Save
    add_instance(name, api_key, url)
    console.print()
    print_status(f"Instance [{RL_ACCENT}]{name}[/] connected and set as active.", style="success")
    console.print()


def _show_active_instance() -> None:
    """Show which instance is active in the banner area."""
    active = get_active_instance_name()
    if active:
        instance = get_active_instance()
        url = instance.get("url", "") if instance else ""
        label = f"{active}"
        if url:
            label += f" [{RL_DIM}]({url})[/]"
        console.print(f"  [{RL_ACCENT}]▸[/] Active instance: [bold {RL_BLUE}]{label}[/]")
        console.print()


# ── CLI Group ────────────────────────────────────────────────────────────────

class RocketlaneCLI(click.Group):
    """Custom group with first-run detection and error handling."""

    def format_help(self, ctx, formatter):
        print_banner()
        _show_active_instance()
        super().format_help(ctx, formatter)

    def invoke(self, ctx):
        try:
            return super().invoke(ctx)
        except RocketlaneAPIError as exc:
            print_status(f"API Error (HTTP {exc.status_code}): {exc.detail}", style="error")
            raise SystemExit(1)
        except (SystemExit, KeyboardInterrupt, click.exceptions.Exit, click.exceptions.Abort):
            raise
        except Exception as exc:
            print_status(f"Error: {exc}", style="error")
            raise SystemExit(1)


@click.group(cls=RocketlaneCLI)
@click.version_option(package_name="rocketlane-cli")
@click.option("--api-key", envvar="ROCKETLANE_API_KEY", help="Override API key")
@click.option("--instance", "-i", help="Use a specific instance by short name")
@click.pass_context
def cli(ctx, api_key, instance):
    """Rocketlane CLI — Professional Services Automation from the terminal."""
    ctx.ensure_object(dict)

    # If switching instance via flag
    if instance:
        try:
            switch_instance(instance)
        except KeyError:
            print_status(f"Instance '{instance}' not found. Run: rocketlane instances", style="error")
            raise SystemExit(1)

    ctx.obj["_api_key_override"] = api_key

    # First-run detection: no instances and no env override, and not running setup commands
    skip_commands = ("add-instance", "instances", "configure", "switch", "schema")
    if ctx.invoked_subcommand not in skip_commands and not api_key:
        key = get_api_key()
        if key is None:
            _first_run_setup()
            if ctx.invoked_subcommand is None:
                raise SystemExit(0)


# ── Instance management commands ─────────────────────────────────────────────

@cli.command("add-instance")
def cmd_add_instance():
    """Add a new Rocketlane instance."""
    print_banner()
    _prompt_add_instance()


@cli.command("switch")
def cmd_switch():
    """Switch between Rocketlane instances."""
    instances = get_instances()
    if not instances:
        print_status("No instances configured. Run: rocketlane add-instance", style="error")
        raise SystemExit(1)

    active = get_active_instance_name()

    console.print()
    console.print(f"  [{RL_ACCENT}]Select an instance:[/]")
    console.print()

    names = list(instances.keys())
    for idx, name in enumerate(names, 1):
        inst = instances[name]
        url = inst.get("url", "")
        marker = "[bold green] ● [/]" if name == active else "   "
        url_display = f" [{RL_DIM}]({url})[/]" if url else ""
        console.print(f"  {marker}[bold]{idx}[/]. [{RL_BLUE}]{name}[/]{url_display}")

    console.print()
    choice = Prompt.ask(
        f"  [{RL_ACCENT}]Enter number[/]",
        choices=[str(i) for i in range(1, len(names) + 1)],
    )

    selected = names[int(choice) - 1]
    switch_instance(selected)
    console.print()
    print_status(f"Switched to [{RL_ACCENT}]{selected}[/]", style="success")
    console.print()


@cli.command("instances")
def cmd_instances():
    """List all configured Rocketlane instances."""
    instances = get_instances()
    active = get_active_instance_name()

    if not instances:
        print_status("No instances configured. Run: rocketlane add-instance", style="info")
        return

    console.print()
    table = Table(
        title="Rocketlane Instances",
        box=box.ROUNDED,
        border_style=RL_DIM,
        header_style=f"bold {RL_ACCENT}",
        title_style=f"bold {RL_BLUE}",
    )
    table.add_column("", width=3)
    table.add_column("Name", style=f"bold {RL_BLUE}")
    table.add_column("URL")
    table.add_column("API Key")

    for name, inst in instances.items():
        marker = "[bold green]●[/]" if name == active else ""
        key = inst.get("api_key", "")
        masked = f"{key[:6]}...{key[-4:]}" if len(key) > 10 else "***"
        table.add_row(marker, name, inst.get("url", ""), masked)

    console.print(table)
    console.print()


@cli.command("remove-instance")
@click.argument("name")
@click.confirmation_option(prompt="Are you sure you want to remove this instance?")
def cmd_remove_instance(name):
    """Remove a configured instance."""
    try:
        remove_instance(name)
        print_status(f"Instance '{name}' removed.", style="success")
    except KeyError as exc:
        print_status(str(exc), style="error")


# ── Status ───────────────────────────────────────────────────────────────────

@cli.command()
@click.pass_context
def status(ctx):
    """Check API connectivity and authentication."""
    print_banner()
    _show_active_instance()
    try:
        key = ctx.obj.get("_api_key_override") or get_api_key()
        if not key:
            print_status("No API key configured. Run: rocketlane add-instance", style="error")
            return
        client = RocketlaneClient(api_key=key)
        data = client.get("/users", limit=1)
        print_status("Connected to Rocketlane API", style="success")
        rows = data.get("data", data) if isinstance(data, dict) else data
        if isinstance(rows, list) and rows:
            user = rows[0]
            name = f"{user.get('firstName', '')} {user.get('lastName', '')}".strip()
            if name:
                print_status(f"Authenticated as {name}", style="info")
            else:
                print_status("Authenticated", style="info")
        else:
            print_status("Authenticated", style="info")
    except RocketlaneAPIError as exc:
        print_status(f"Authentication failed (HTTP {exc.status_code})", style="error")
    except Exception as exc:
        print_status(f"Connection failed: {exc}", style="error")


# ── Legacy configure (kept for backwards compat) ────────────────────────────

@cli.command("configure", hidden=True)
@click.option("--key", prompt="Rocketlane API Key", hide_input=True, help="Your API key")
def configure(key):
    """Save your Rocketlane API key locally (legacy)."""
    add_instance("default", key, "")
    print_status("API key saved.", style="success")


# ── Register all command groups ──────────────────────────────────────────────

cli.add_command(projects)
cli.add_command(tasks)
cli.add_command(phases)
cli.add_command(fields)
cli.add_command(users)
cli.add_command(spaces)
cli.add_command(documents)
cli.add_command(time_tracking)
cli.add_command(time_offs)
cli.add_command(resource_allocations)
cli.add_command(invoices)
cli.add_command(schema)
cli.add_command(api)


def main():
    cli()


if __name__ == "__main__":
    main()
