#!/bin/bash

# Aphrodite v2 Docker Entrypoint Script

set -e

# Color output functions
red() { echo -e "\033[31m$1\033[0m"; }
green() { echo -e "\033[32m$1\033[0m"; }
yellow() { echo -e "\033[33m$1\033[0m"; }
blue() { echo -e "\033[34m$1\033[0m"; }

echo "🚀 Starting Aphrodite v2 Container"
echo "=================================="

# Handle user permissions if PUID/PGID are set
if [ "$PUID" != "1000" ] || [ "$PGID" != "1000" ]; then
    yellow "Setting up user permissions (PUID=$PUID, PGID=$PGID)"
    
    # Modify the group ID
    groupmod -o -g "$PGID" aphrodite
    
    # Modify the user ID  
    usermod -o -u "$PUID" aphrodite
    
    # Fix ownership
    chown -R aphrodite:aphrodite /app
fi

# Create/fix directory permissions
green "Setting up directories and permissions"
mkdir -p /app/api/static/processed \
         /app/api/cache/posters \
         /app/media \
         /app/logs \
         /app/temp

chown -R aphrodite:aphrodite /app/api/static \
                              /app/api/cache \
                              /app/media \
                              /app/logs \
                              /app/temp

# Function to run as aphrodite user
run_as_user() {
    gosu aphrodite "$@"
}

# Handle the command
case "$1" in
    "api")
        green "Starting Aphrodite v2 API Server"
        cd /app
        exec run_as_user python start_api.py
        ;;
        
    "worker")
        green "Starting Aphrodite v2 Celery Worker"
        cd /app
        exec run_as_user python start_worker.py
        ;;
        
    "frontend")
        green "Starting Aphrodite v2 Frontend Development Server"
        if [ -d "/app/frontend" ]; then
            cd /app/frontend
            exec run_as_user npm run dev
        else
            red "Frontend directory not found"
            exit 1
        fi
        ;;
        
    "bash")
        green "Starting interactive bash shell"
        exec run_as_user bash
        ;;
        
    *)
        green "Running custom command: $*"
        exec run_as_user "$@"
        ;;
esac
