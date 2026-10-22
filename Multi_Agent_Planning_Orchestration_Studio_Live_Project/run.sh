#!/bin/bash
# Multi-Agent Planning & Orchestration Studio — Launch Script
# Port: 8210

PORT=8210
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_EXEC="/home/hemanth/jupyterenv/bin/python"

echo "=========================================================="
echo "🚀 Starting Multi-Agent Planning & Orchestration Studio"
echo "   Directory: $PROJECT_DIR"
echo "   Port:      $PORT"
echo "=========================================================="

# Check and free port if occupied
PID=$(lsof -ti :$PORT 2>/dev/null)
if [ ! -z "$PID" ]; then
    echo "⚠️ Port $PORT is occupied by PID $PID. Terminating process..."
    kill -9 $PID 2>/dev/null
    sleep 1
fi

# Ensure database exists
if [ ! -f "$PROJECT_DIR/data/enterprise_database.sqlite" ]; then
    echo "📦 Initializing enterprise database..."
    $PYTHON_EXEC "$PROJECT_DIR/data/init_sqlite_db.py"
fi

# Start FastAPI application
cd "$PROJECT_DIR"
exec $PYTHON_EXEC -m uvicorn app:app --host 0.0.0.0 --port $PORT
