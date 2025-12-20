#!/bin/bash
# Stop all Celery workers

echo "🛑 Stopping all Celery workers..."

# Kill all processes matching "celery"
echo "Searching for Celery processes..."
PIDS=$(pgrep -f "celery")

if [ -z "$PIDS" ]; then
    echo "No Celery workers found running."
else
    echo "Found PIDs: $PIDS"
    echo "Killing..."
    kill -9 $PIDS
    echo "✅ Killed all Celery processes."
fi

# Double check
sleep 1
REMAINING=$(pgrep -f "celery")
if [ -n "$REMAINING" ]; then
    echo "⚠️ Warning: Some processes still running: $REMAINING"
else
    echo "✅ Verified: No Celery processes running."
fi
