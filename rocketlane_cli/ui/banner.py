"""Startup banner and terminal UI styling for Rocketlane CLI."""

from rich.console import Console
from rich.text import Text

from rocketlane_cli import __version__

console = Console()

# Rocketlane brand colors
RL_BLUE = "#3D5AFE"
RL_WHITE = "#FFFFFF"
RL_GRAY = "#8892B0"
RL_DIM = "#4A5568"
RL_ACCENT = "#7C8AFF"

# The double-chevron logo mark + "ROCKETLANE CLI" in a blocky pixel style
# Inspired by the Rocketlane brand chevron mark
LOGO = r"""
[bold {blue}]  ██████╗  ██████╗  ██████╗██╗  ██╗███████╗████████╗██╗      █████╗ ███╗   ██╗███████╗[/]
[bold {blue}]  ██╔══██╗██╔═══██╗██╔════╝██║ ██╔╝██╔════╝╚══██╔══╝██║     ██╔══██╗████╗  ██║██╔════╝[/]
[bold {accent}]  ██████╔╝██║   ██║██║     █████╔╝ █████╗     ██║   ██║     ███████║██╔██╗ ██║█████╗  [/]
[bold {accent}]  ██╔══██╗██║   ██║██║     ██╔═██╗ ██╔══╝     ██║   ██║     ██╔══██║██║╚██╗██║██╔══╝  [/]
[bold {white}]  ██║  ██║╚██████╔╝╚██████╗██║  ██╗███████╗   ██║   ███████╗██║  ██║██║ ╚████║███████╗[/]
[bold {white}]  ╚═╝  ╚═╝ ╚═════╝  ╚═════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝╚══════╝[/]
""".format(blue=RL_BLUE, accent=RL_ACCENT, white=RL_WHITE)

CHEVRON = r"""
[bold {blue}]  ╔══╗ ╔══╗[/]
[bold {blue}]  ╚╗╔╝ ╚╗╔╝[/]
[bold {accent}]   ╚╝   ╚╝ [/]
[bold {accent}]   ╔╗   ╔╗ [/]
[bold {white}]  ╔╝╚╗ ╔╝╚╗[/]
[bold {white}]  ╚══╝ ╚══╝[/]
""".format(blue=RL_BLUE, accent=RL_ACCENT, white=RL_WHITE)

TAGLINE = "[{gray}]Professional Services Automation — CLI[/]".format(gray=RL_GRAY)
VERSION_TAG = "[{dim}]v{ver}[/]".format(dim=RL_DIM, ver=__version__)


def print_banner() -> None:
    """Print the startup banner with logo and version."""
    console.print()

    # Chevron mark + wordmark side by side
    logo_text = Text.from_markup(LOGO)
    console.print(logo_text)

    # CLI subtitle line
    sub = Text.from_markup(
        "  [{blue}]»»[/] [{accent}]CLI[/]  {tagline}  {ver}".format(
            blue=RL_BLUE, accent=RL_ACCENT, tagline=TAGLINE, ver=VERSION_TAG,
        )
    )
    console.print(sub)
    console.print()


def print_status(message: str, style: str = "info") -> None:
    """Print a styled status message."""
    styles = {
        "info": RL_ACCENT,
        "success": "#00C853",
        "warning": "#FFD600",
        "error": "#FF1744",
    }
    color = styles.get(style, RL_ACCENT)
    icons = {"info": "●", "success": "✓", "warning": "▲", "error": "✗"}
    icon = icons.get(style, "●")
    console.print(f"  [{color}]{icon}[/] {message}")
