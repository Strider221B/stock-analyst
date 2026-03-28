#!/bin/bash
# Exit on error
set -e

echo "Running Frontend Tests..."
cd frontend
npm run test

if [ $? -eq 0 ]; then
    echo "Frontend tests passed."
    exit 0
else
    echo "Frontend tests failed."
    exit 1
fi
