.PHONY: install install-dev run serve test lint clean

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

run:
	python examples/01_basic/run.py

serve:
	agent-starter serve

chat:
	agent-starter chat

test:
	pytest tests/ -v --tb=short

lint:
	ruff check agent_starter/ tests/ || true
	ruff format --check agent_starter/ tests/ || true

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	rm -rf .agentkit/ dist/ build/ *.egg-info
