#!/bin/bash
# Docker Startup Script for Aphrodite Production
#
# This script handles database initialization and starts the FastAPI application.

echo "🚀 Starting Aphrodite v4.0.0 Production Container"
echo "================================================"

# Wait for database to be ready
echo "⏳ Waiting for database connection..."
while ! python -c "
import asyncio
import sys
import os
sys.path.insert(0, '/app')
try:
    from api.app.core.database import DatabaseManager
    result = asyncio.run(DatabaseManager.health_check())
    if result['status'] != 'healthy':
        exit(1)
    print('✅ Database connection established')
except Exception as e:
    print(f'❌ Database not ready: {e}')
    exit(1)
"; do
    echo "  Retrying in 5 seconds..."
    sleep 5
done

# Initialize database tables and default settings
echo "🔧 Initializing database..."
python -c "
import asyncio
import sys
sys.path.insert(0, '/app')
from api.app.core.database import init_db
asyncio.run(init_db())
print('✅ Database tables initialized')
"

# Initialize badge settings if this is a fresh installation
echo "⚙️  Checking for default settings..."
python init-badge-settings-production.py

echo "🌟 Starting Aphrodite API Server..."
exec python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 1
