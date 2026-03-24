"""Shared CLI utilities — lazy client initialization."""

from __future__ import annotations

import click

from rocketlane_cli.client import RocketlaneClient


def get_client(ctx: click.Context) -> RocketlaneClient:
    """Lazily create and cache the API client from click context."""
    obj = ctx.find_root().obj
    if obj is None:
        obj = {}
        ctx.find_root().obj = obj
    if "client" not in obj:
        obj["client"] = RocketlaneClient(api_key=obj.get("_api_key_override"))
    return obj["client"]
