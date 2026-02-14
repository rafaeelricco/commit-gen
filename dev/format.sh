#!/bin/bash

# Format script for commit-gen project
# Uses ruff for fast Python formatting

set -e  # Exit on any error

echo "| Running formatter with ruff..."

# Ensure ruff is in dev dependencies
if ! uv tree | grep -q "ruff"; then
    echo " ruff not found in dependencies. Adding..."
    uv add --dev ruff
fi

# Run ruff format
echo "S Formatting code..."
uv run ruff format src/

echo ", Formatting completed successfully!"
