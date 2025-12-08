#!/bin/bash

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"

# Source environment variables
source "$PROJECT_ROOT/local-env.sh"

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Run Flower
echo "🌸 Starting Flower on http://localhost:5555"
cd "$PROJECT_ROOT/response-network/api"
celery -A workers.celery_app flower --port=5555
