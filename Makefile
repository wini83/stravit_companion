.DEFAULT_GOAL := help

.PHONY: help sync lint format test coverage check run refresh dry-run diff chart distance-chart docker-build docker-run

help:
	@echo "Available targets:"
	@echo "  make sync         Install and synchronize dependencies"
	@echo "  make lint         Run Ruff checks"
	@echo "  make format       Format Python code with Ruff"
	@echo "  make test         Run the test suite"
	@echo "  make coverage     Run tests with the configured coverage threshold"
	@echo "  make check        Run lint and tests"
	@echo "  make run          Run against stored snapshots"
	@echo "  make refresh      Fetch a fresh snapshot and run alert detection"
	@echo "  make dry-run      Refresh and detect alerts without sending them"
	@echo "  make diff         Compare snapshots (FROM=latest-1 TO=latest)"
	@echo "  make chart        Generate rank history (TOP=10 OUTPUT=ranking.png)"
	@echo "  make distance-chart Generate distance history (TOP=10 OUTPUT=distance.png)"
	@echo "  make docker-build Build the local Docker image"
	@echo "  make docker-run   Run the application with Docker Compose"

sync:
	uv sync --frozen

lint:
	uv run ruff check .

format:
	uv run ruff format .

test:
	uv run python -m pytest

coverage:
	uv run python -m pytest --cov=stravit_companion --cov-report=term-missing --cov-report=xml

check: lint test

run:
	uv run python -m stravit_companion.runner

refresh:
	uv run python -m stravit_companion.runner --refresh

dry-run:
	uv run python -m stravit_companion.runner --refresh --dry-run

diff:
	uv run python -m stravit_companion.runner diff $(or $(FROM),latest-1) $(or $(TO),latest)

chart:
	uv run python -m stravit_companion.runner charts ranking-history --top $(or $(TOP),10) --output $(or $(OUTPUT),ranking.png)

distance-chart:
	uv run python -m stravit_companion.runner charts distance-history --top $(or $(TOP),10) --output $(or $(OUTPUT),distance.png)

docker-build:
	docker compose -f docker-compose.dev.yml build

docker-run:
	docker compose run --rm stravit
