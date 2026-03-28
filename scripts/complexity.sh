#!/bin/bash

# Running radon (success if complexity ≤ 10 for all functions)
echo "Running Radon for Cyclomatic Complexity..."

# Radon CC results: A (1-5), B (6-10), C (11-20), etc.
# Success only if all are A or B (i.e. rank ≤ 10)
RESULTS=$(radon cc backend/ -n C)

if [ -n "$RESULTS" ]; then
    echo "Found functions with cyclomatic complexity greater than 10:"
    echo "$RESULTS"
    exit 1
else
    echo "Cyclomatic complexity checks passed (all ≤ 10)."
    exit 0
fi
