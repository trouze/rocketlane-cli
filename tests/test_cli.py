"""Smoke tests for the rocketlane CLI."""

from click.testing import CliRunner
from rocketlane_cli.cli import main


def test_help():
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "rocketlane" in result.output.lower() or "Usage" in result.output


def test_projects_help():
    runner = CliRunner()
    result = runner.invoke(main, ["projects", "--help"])
    assert result.exit_code == 0


def test_tasks_help():
    runner = CliRunner()
    result = runner.invoke(main, ["tasks", "--help"])
    assert result.exit_code == 0


def test_time_help():
    runner = CliRunner()
    result = runner.invoke(main, ["time", "--help"])
    assert result.exit_code == 0


def test_version():
    from rocketlane_cli import __version__
    assert __version__ == "0.1.0"
