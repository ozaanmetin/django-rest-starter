.PHONY: help install install-dev sync lock update lint format test test-cov migrate migrations \
	run shell celery celery-beat docker-up docker-down docker-build clean check \
	pre-commit-install pre-commit-staged pre-commit-run pre-commit-update pre-commit-clean

# Colors
YELLOW := \033[1;33m
GREEN := \033[1;32m
NC := \033[0m

# Default target
help:
	@echo "$(GREEN)Django REST Starter - Development Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Setup:$(NC)"
	@echo "  make install          - Install production dependencies"
	@echo "  make sync             - Sync dependencies with lockfile"
	@echo "  make lock             - Generate/update uv.lock"
	@echo "  make update           - Update all dependencies"
	@echo ""
	@echo "$(YELLOW)Development:$(NC)"
	@echo "  make run              - Run development server"
	@echo "  make shell            - Open Django shell (IPython)"
	@echo "  make migrate          - Run database migrations"
	@echo "  make migrations       - Create new migrations"
	@echo "  make superuser        - Create superuser"
	@echo "  make collectstatic    - Collect static files"
	@echo ""
	@echo "$(YELLOW)Code Quality:$(NC)"
	@echo "  make lint             - Run ruff linter"
	@echo "  make lint-fix         - Run ruff linter with auto-fix"
	@echo "  make format           - Format code with ruff"
	@echo "  make format-check     - Check code formatting"
	@echo "  make security         - Run bandit security check"
	@echo "  make check            - Run all checks (lint + format + security + test)"
	@echo ""
	@echo "$(YELLOW)Testing:$(NC)"
	@echo "  make test             - Run tests"
	@echo "  make test-cov         - Run tests with coverage"
	@echo "  make test-verbose     - Run tests with verbose output"
	@echo ""
	@echo "$(YELLOW)Celery:$(NC)"
	@echo "  make celery           - Run Celery worker"
	@echo "  make celery-beat      - Run Celery beat scheduler"
	@echo ""
	@echo "$(YELLOW)Docker:$(NC)"
	@echo "  make docker-up        - Start all services"
	@echo "  make docker-down      - Stop all services"
	@echo "  make docker-build     - Build Docker images"
	@echo "  make docker-logs      - View Docker logs"
	@echo ""
	@echo "$(YELLOW)Utilities:$(NC)"
	@echo "  make outdated         - Show outdated packages"
	@echo "  make requirements     - Export to requirements.txt"

# Setup
install:
	uv sync
	uv run pre-commit install

sync:
	uv sync

lock:
	uv lock

update:
	uv lock --upgrade
	uv sync

# Development

run:
	uv run python manage.py runserver

shell:
	uv run python manage.py shell -i ipython

migrate:
	uv run python manage.py migrate

migrations:
	uv run python manage.py makemigrations

superuser:
	uv run python manage.py createsuperuser

collectstatic:
	uv run python manage.py collectstatic --noinput

# Code Quality

lint:
	uv run ruff check .

lint-fix:
	uv run ruff check . --fix

format:
	uv run ruff format .

format-check:
	uv run ruff format . --check

security:
	uv run bandit -c pyproject.toml -r apps/

check: lint-fix format security test
	@echo "$(GREEN)All checks passed!$(NC)"


# Testing

test:
	uv run pytest

test-cov:
	uv run pytest --cov=apps --cov-report=html --cov-report=term-missing

test-verbose:
	uv run pytest -v --tb=short


# Celery

celery:
	uv run celery -A config worker -l INFO

celery-beat:
	uv run celery -A config beat -l INFO

# Docker
COMPOSE_CMD = docker compose -f docker-compose.yaml --env-file .env

docker-up:
	$(COMPOSE_CMD) up -d

docker-down:
	$(COMPOSE_CMD) down

docker-build:
	$(COMPOSE_CMD) build

docker-logs:
	$(COMPOSE_CMD) logs -fn$(lines) $(service)

docker-restart:
	$(COMPOSE_CMD) up -d --build --force-recreate

docker-superuser:
	$(COMPOSE_CMD) exec web python manage.py createsuperuser

# Show outdated packages
outdated:
	uv pip list --outdated


# Export to requirements.txt
requirements:
	uv pip compile pyproject.toml --extra sentry --extra otel -o requirements.txt
