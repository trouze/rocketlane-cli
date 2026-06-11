.PHONY: sync-spec test lint

sync-spec:
	uv run scripts/sync_spec.py

test:
	uv run pytest tests/

lint:
	uv run ruff check rocketlane_cli/
