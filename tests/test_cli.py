"""Smoke tests for the rocketlane CLI."""

from click.testing import CliRunner
from rocketlane_cli.cli import cli


_ENV = {"ROCKETLANE_API_KEY": "test-key"}


def test_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"], env=_ENV)
    assert result.exit_code == 0


def test_projects_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["projects", "--help"], env=_ENV)
    assert result.exit_code == 0


def test_tasks_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["tasks", "--help"], env=_ENV)
    assert result.exit_code == 0


def test_time_help():
    runner = CliRunner()
    result = runner.invoke(cli, ["time", "--help"], env=_ENV)
    assert result.exit_code == 0


def test_version():
    from rocketlane_cli import __version__
    assert __version__ == "0.1.0"
