#!/bin/bash

# Exit on error
set -e

# Run conditionally if we are not in CI
if [ "$CI" != "true" ]; then
    echo "Activating Python environment..."
    source ~/python_envs/p3_13_llm/bin/activate
fi

# Spin up a temporary postgres container for testing
echo "Starting test database container..."
docker run --name stock-analyzer-test-db \
    -e POSTGRES_USER=postgres \
    -e POSTGRES_PASSWORD=postgres \
    -e POSTGRES_DB=stock_analyzer_test \
    -p 5433:5432 \
    -d postgres:15

# Ensure we tear down the container when this script exits
cleanup() {
    echo "Tearing down test database container..."
    docker stop stock-analyzer-test-db || true
    docker rm stock-analyzer-test-db || true
}
trap cleanup EXIT

# Wait for database to be ready
echo "Waiting for test database to accept connections..."
sleep 3

export TEST_DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5433/stock_analyzer_test"
export API_USER=postgres
export ADMIN_USER=postgres
export DATABASE_URL=$TEST_DATABASE_URL

# Running pytests (success only if all tests pass and coverage is met)
echo "Running Pytests..."
PYTHONPATH=backend pytest backend/ --cov=backend --cov-fail-under=80 -v

if [ $? -eq 0 ]; then
    echo "Pytests passed."
    exit 0
else
    echo "Pytests failed."
    exit 1
fi
