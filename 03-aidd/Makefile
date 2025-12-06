.PHONY: run install lint test clean

run:
	uv run python -m src.cook_assistant.bot

install:
	uv sync

lint:
	uv run ruff check .

test:
	uv run pytest

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache