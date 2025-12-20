#!/bin/bash
# Startup script for Request and Response Network Workers
# Usage: ./START_WORKERS.sh

# Detect Project Root
PROJECT_ROOT="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "🚀 Starting Workers from: $PROJECT_ROOT"

# Create log directory
mkdir -p /tmp/worker_logs

# Function to start a worker
start_worker() {
    local name=$1
    local dir=$2
    local app=$3
    local logfile="/tmp/worker_logs/${name}.log"

    echo "Starting $name..."
    cd "$PROJECT_ROOT/$dir" || exit
    
    # Use standard python execution
    nohup python3 -m celery -A $app worker --beat --loglevel=info > "$logfile" 2>&1 &
    
    echo "✅ $name started! (PID: $!) | Logs: $logfile"
}

# Start Request Network Worker
start_worker "request-network" "request-network/api" "workers.celery_app"

# Start Response Network Worker
start_worker "response-network" "response-network/api" "workers.celery_app"

echo ""
echo "=============================================="
echo "🎉 All Systems Go!"
echo "Use 'tail -f /tmp/worker_logs/*.log' to monitor."
echo "=============================================="
