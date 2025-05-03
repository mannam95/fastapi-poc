.PHONY: up down logs test lint format migrations migrate build shell clean help test-unit test-integration

# Docker commands
up:
	docker compose -f docker/docker-compose.yml up

down:
	docker compose -f docker/docker-compose.yml down

logs:
	docker compose -f docker/docker-compose.yml logs -f

build:
	docker compose -f docker/docker-compose.yml build

# Test commands
test-build:
	docker compose -f docker/docker-compose.test.yml build

test:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc pytest
	docker compose -f docker/docker-compose.test.yml down

test-cov:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc pytest --cov=app --cov-report=term-missing
	docker compose -f docker/docker-compose.test.yml down

test-unit:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc pytest -m unit
	docker compose -f docker/docker-compose.test.yml down

test-integration:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc pytest -m integration
	docker compose -f docker/docker-compose.test.yml down

# Database commands
migrations:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc alembic revision --autogenerate -m "$(m)"

migrate:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc alembic upgrade head

# Code quality
lint:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc black app tests
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc isort app tests
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc flake8 app tests
	docker compose -f docker/docker-compose.test.yml down

format:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc black app tests
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc isort app tests
	docker compose -f docker/docker-compose.test.yml down

mypy:
	docker compose -f docker/docker-compose.test.yml run --rm test-fast-api-poc mypy app
	docker compose -f docker/docker-compose.test.yml down

nuke:
	docker compose -f docker/docker-compose.yml down
	docker compose -f docker/docker-compose.test.yml down
	docker volume prune -f
	docker system prune -f
	sudo rm -rf postgres-data docker/postgres-data
	sudo rm -rf test-postgres-data docker/test-postgres-data
	sudo rm -rf .pytest_cache
	sudo rm -rf .coverage
	sudo find . -type d -name __pycache__ -exec rm -rf {} +
	sudo find . -type f -name "*.pyc" -delete
	sudo find . -type f -name "*.pyo" -delete
	sudo find . -type f -name "*.pyd" -delete
	sudo find . -type f -name ".coverage" -delete
	sudo find . -type d -name "*.egg-info" -exec rm -rf {} +
	sudo find . -type d -name "*.egg" -exec rm -rf {} +
	sudo find . -type d -name ".pytest_cache" -exec rm -rf {} +
	sudo find . -type d -name ".coverage" -exec rm -rf {} +
	sudo find . -type d -name "htmlcov" -exec rm -rf {} +
	sudo find . -type d -name ".mypy_cache" -exec rm -rf {} +
	sudo rm -rf build/
	sudo rm -rf dist/

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
	@echo "  nuke            Delete all temporary files"