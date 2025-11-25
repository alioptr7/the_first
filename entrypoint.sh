#!/bin/bash
# Entrypoint script for Response Network API
set -e

export PYTHONPATH="/app:${PYTHONPATH}"

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
for i in {1..30}; do
    if python -c "import psycopg2; psycopg2.connect('dbname=response_network user=postgres password=postgres host=db port=5432')" 2>/dev/null; then
        echo "✓ Database is ready"
        break
    fi
    echo "Attempt $i/30 - Database not ready yet..."
    sleep 2
done

# Initialize database
echo "📦 Initializing Response Network database..."
cd /app/response-network/api
python manage.py init || true
python manage.py migrate || true
python manage.py seed || true

echo "✓ Initialization complete"
echo "🚀 Starting FastAPI server..."

# Run the main FastAPI app
exec python -m uvicorn main:app --host 0.0.0.0 --port 8000
