#!/bin/bash

# Running all pytests (success only if all tests pass)
echo "Running Pytests..."
pytest backend/

if [ $? -eq 0 ]; then
    echo "Pytests passed."
    exit 0
else
    echo "Pytests failed."
    exit 1
fi
