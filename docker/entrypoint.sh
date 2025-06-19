#!/bin/bash
set -e

# Function to log messages
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# Function to wait for service
wait_for_service() {
    local host=$1
    local port=$2
    local service=$3
    local timeout=${4:-30}
    
    log "Waiting for $service at $host:$port..."
    
    for i in $(seq 1 $timeout); do
        if nc -z "$host" "$port" 2>/dev/null; then
            log "$service is ready!"
            return 0
        fi
        log "Waiting for $service... ($i/$timeout)"
        sleep 1
    done
    
    log "ERROR: $service is not available after $timeout seconds"
    exit 1
}

# Function to handle user permissions
setup_permissions() {
    # Get current user/group IDs
    CURRENT_UID=$(id -u aphrodite)
    CURRENT_GID=$(id -g aphrodite)
    
    # If PUID/PGID are set and different from current, update them
    if [ ! -z "$PUID" ] && [ "$PUID" != "$CURRENT_UID" ]; then
        log "Updating user ID from $CURRENT_UID to $PUID"
        usermod -u "$PUID" aphrodite
    fi
    
    if [ ! -z "$PGID" ] && [ "$PGID" != "$CURRENT_GID" ]; then
        log "Updating group ID from $CURRENT_GID to $PGID"
        groupmod -g "$PGID" aphrodite
    fi
    
    # Ensure ownership of important directories
    chown -R aphrodite:aphrodite /app/media /app/logs /app/temp /app/config /app/cache /app/images 2>/dev/null || true
}

# Function to run database migrations and setup
setup_database() {
    log "Setting up database..."
    
    # Wait for PostgreSQL to be ready
    if [ ! -z "$DATABASE_URL" ]; then
        # Extract host and port from DATABASE_URL
        DB_HOST=$(echo $DATABASE_URL | sed -n 's/.*@\([^:]*\):.*/\1/p')
        DB_PORT=$(echo $DATABASE_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ ! -z "$DB_HOST" ] && [ ! -z "$DB_PORT" ]; then
            wait_for_service "$DB_HOST" "$DB_PORT" "PostgreSQL" 60
        fi
    fi
    
    # Run database migrations/setup as the aphrodite user
    gosu aphrodite python -c "
import asyncio
import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/api')

async def setup_db():
    try:
        from api.app.core.database import init_db
        await init_db()
        print('Database initialization completed successfully')
    except Exception as e:
        print(f'Database initialization failed: {e}')
        raise

asyncio.run(setup_db())
"
}

# Function to setup Redis connection
setup_redis() {
    if [ ! -z "$REDIS_URL" ]; then
        # Extract host and port from REDIS_URL
        REDIS_HOST=$(echo $REDIS_URL | sed -n 's/.*@\([^:]*\):.*/\1/p' | sed 's/.*\/\/[^@]*@\?\([^:]*\).*/\1/')
        REDIS_PORT=$(echo $REDIS_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
        
        if [ -z "$REDIS_HOST" ]; then
            REDIS_HOST=$(echo $REDIS_URL | sed 's/redis:\/\/[^@]*@\?\([^:\/]*\).*/\1/')
        fi
        
        if [ -z "$REDIS_PORT" ]; then
            REDIS_PORT=6379
        fi
        
        if [ ! -z "$REDIS_HOST" ]; then
            wait_for_service "$REDIS_HOST" "$REDIS_PORT" "Redis" 30
        fi
    fi
}

# Main execution
main() {
    log "Starting Aphrodite v2 container..."
    log "Build environment: ${BUILD_ENV:-production}"
    log "Command: $1"
    
    # Setup permissions first
    setup_permissions
    
    # Install netcat if not present (for service checks)
    if ! command -v nc &> /dev/null; then
        apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*
    fi
    
    case "$1" in
        "api")
            log "Starting API server..."
            setup_redis
            setup_database
            
            # Start the API server as aphrodite user
            cd /app/api
            exec gosu aphrodite python main.py
            ;;
            
        "celery-worker")
            log "Starting Celery worker..."
            setup_redis
            
            # Start Celery worker as aphrodite user
            cd /app/api
            exec gosu aphrodite celery -A celery_app worker --loglevel=info --concurrency=4
            ;;
            
        "celery-beat")
            log "Starting Celery beat scheduler..."
            setup_redis
            
            # Start Celery beat as aphrodite user
            cd /app/api
            exec gosu aphrodite celery -A celery_app beat --loglevel=info
            ;;
            
        "shell")
            log "Starting interactive shell..."
            setup_permissions
            exec gosu aphrodite /bin/bash
            ;;
            
        "migrate")
            log "Running database migrations..."
            setup_database
            log "Migrations completed"
            ;;
            
        "test")
            log "Running tests..."
            setup_permissions
            cd /app/api
            exec gosu aphrodite python -m pytest
            ;;
            
        *)
            log "Unknown command: $1"
            log "Available commands: api, celery-worker, celery-beat, shell, migrate, test"
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
