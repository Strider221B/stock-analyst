#!/bin/bash

# Running all check scripts in the script folder
echo "Running All Checks..."

./scripts/test.sh && \
./scripts/test-frontend.sh && \
# ./scripts/lint.sh && \
# ./scripts/type-check.sh

if [ $? -eq 0 ]; then
    echo "All checks passed successfully."
    exit 0
else
    echo "Some checks failed. See output above for details."
    exit 1
fi
