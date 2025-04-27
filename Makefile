.PHONY: up down logs test lint format migrations migrate build shell clean help test-unit test-integration

# Docker commands
up:
	docker compose up

down:
	docker compose down

logs:
	docker compose logs -f

build:
	docker compose build

# Test commands
test-build:
	docker compose -f docker-compose.test.yml build

test:
	docker compose -f docker-compose.test.yml run --rm test-api pytest

test-cov:
	docker compose -f docker-compose.test.yml run --rm test-api pytest --cov=app --cov-report=term-missing

test-unit:
	docker compose -f docker-compose.test.yml run --rm test-api pytest -m unit

test-integration:
	docker compose -f docker-compose.test.yml run --rm test-api pytest -m integration

# Database commands
migrations:
	docker compose run --rm api alembic revision --autogenerate -m "$(m)"

migrate:
	docker compose run --rm api alembic upgrade head

# Code quality
lint:
	docker compose run --rm api black app tests
	docker compose run --rm api isort app tests
	docker compose run --rm api flake8 app tests

format:
	docker compose run --rm api black app tests
	docker compose run --rm api isort app tests

mypy:
	docker compose run --rm api mypy app

# Shell
shell:
	docker compose run --rm api python

clean:
	docker compose down
	docker compose -f docker-compose.test.yml down
	docker volume prune -f
	docker system prune -f
	sudo rm -rf postgres-data
	sudo rm -rf test-postgres-data
# Help
help:
	@echo "Available commands:"
	@echo "  up              Start the application"
	@echo "  down            Stop the application"
	@echo "  logs            Show logs"
	@echo "  build           Build Docker images"
	@echo "  test            Run tests"
	@echo "  test-cov        Run tests with coverage"
	@echo "  test-unit       Run unit tests"
	@echo "  test-integration Run integration tests"
	@echo "  migrations m='' Create a new migration"
	@echo "  migrate         Apply migrations"
	@echo "  lint            Run linters"
	@echo "  format          Format code"
	@echo "  mypy            Run type checking"
	@echo "  shell           Open Python shell"
	@echo "  clean           Remove temporary files"