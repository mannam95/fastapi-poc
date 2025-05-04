#!/bin/bash
set -e

# Start the docker compose test environment
echo "Starting the test environment..."
docker compose -f docker/docker-compose.test.yml up -d

# Determine which commands to run based on the first parameter
COMMANDS="python -m app.core.db_init"

if [ "$1" = "lint" ]; then
    echo "Running linting commands..."
    COMMANDS="$COMMANDS && black app tests && isort app tests && flake8 app tests"
    shift
elif [ "$1" = "format" ]; then
    echo "Running formatting commands..."
    COMMANDS="$COMMANDS && black app tests && isort app tests"
    shift
elif [ "$1" = "mypy" ]; then
    echo "Running mypy commands..."
    COMMANDS="$COMMANDS && mypy app"
    shift
elif [ "$1" = "test" ]; then
    echo "Running test commands..."
    COMMANDS="$COMMANDS && pytest"
    shift
elif [ "$1" = "test-cov" ]; then
    echo "Running test coverage commands..."
    COMMANDS="$COMMANDS && pytest --cov=app --cov-report=term-missing"
    shift
elif [ "$1" = "test-unit" ]; then
    echo "Running unit test commands..."
    COMMANDS="$COMMANDS && pytest -m unit"
    shift
elif [ "$1" = "test-integration" ]; then
    echo "Running integration test commands..."
    COMMANDS="$COMMANDS && pytest -m integration"
    shift
elif [ "$1" != "" ]; then
    # If parameter is provided but not a special case, append it to commands
    COMMANDS="$COMMANDS && $*"
fi

# Execute commands inside the container and then exit
echo "Entering container to run commands..."
docker exec -it test-fast-api-poc-con bash -c "$COMMANDS"

# Shutdown the test environment
echo "Shutting down the test application..."
docker compose -f docker/docker-compose.test.yml down
