#!/bin/bash

# Running ruff (success if all checks pass)
# C901: complex-structure check
# --max-complexity 9 means it will fail if complexity >= 10
echo "Running Ruff..."
ruff check backend/ --select ALL --extend-ignore=D,ANN,ERA,FIX,TD --max-complexity 9

if [ $? -eq 0 ]; then
    echo "Ruff checks passed."
    exit 0
else
    echo "Ruff checks failed."
    exit 1
fi
