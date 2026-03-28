#!/bin/bash

# Running pylint (returns success if score greater than 9)
echo "Running Pylint..."

# Run pylint and get the score
SCORE=$(pylint backend/ | grep -oP "Your code has been rated at \K[0-9.]+" | head -n 1)

if [ -z "$SCORE" ]; then
    echo "Pylint failed to run or found no files."
    exit 1
fi

echo "Pylint score: $SCORE"

# Check if score is greater than 9
if (( $(echo "$SCORE > 9" | bc -l) )); then
    echo "Pylint check passed."
    exit 0
else
    echo "Pylint score ($SCORE) is less than or equal to 9."
    exit 1
fi
