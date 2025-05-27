.PHONY: up down logs test lint format migrations migrate build shell clean help test-unit test-integration build-prod

# Docker commands
up:
	docker compose -f docker/docker-compose.yml up

down:
	docker compose -f docker/docker-compose.yml down

logs:
	docker compose -f docker/docker-compose.yml logs -f

build:
	docker compose -f docker/docker-compose.yml build

build-prod:
	docker build -f docker/Dockerfile.prod -t fast-api-poc-prod .

build-locust:
	docker build --no-cache -t sri-locust-poc -f docker/Dockerfile.locust .

push-docker-registry:
	docker build --no-cache  -t mvsrinath/sri-fast-api-poc:latest -f docker/Dockerfile .
	docker build --no-cache  -t mvsrinath/sri-locust-poc:latest -f docker/Dockerfile.locust .
	docker push mvsrinath/sri-fast-api-poc:latest
	docker push mvsrinath/sri-locust-poc:latest

# Test commands
test-build:
	docker compose -f docker/docker-compose.test.yml build

test:
	./docker/start_test.sh test

test-cov:
	./docker/start_test.sh test-cov

test-unit:
	./docker/start_test.sh test-unit

test-integration:
	./docker/start_test.sh test-integration

# Database commands
migrations:
	echo "TODO: Implement migrations"

migrate:
	echo "TODO: Implement migrations"

# Code quality
lint:
	./docker/start_test.sh lint

format:
	./docker/start_test.sh format

mypy:
	./docker/start_test.sh mypy

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
	@echo "  build-prod      Build production Docker image"
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