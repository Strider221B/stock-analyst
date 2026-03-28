#!/bin/bash

# Running mypy (success if all checks pass)
echo "Running Mypy..."
mypy backend/

if [ $? -eq 0 ]; then
    echo "Mypy checks passed."
    exit 0
else
    echo "Mypy checks failed."
    exit 1
fi
