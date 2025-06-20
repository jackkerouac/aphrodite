# Use multi-stage build for production optimization
FROM node:18-slim AS frontend-builder

# Build frontend if it exists
WORKDIR /frontend-build
COPY frontend/package*.json ./
# Install all dependencies (including devDependencies needed for build)
RUN if [ -f package.json ]; then npm ci; fi
COPY frontend/ ./
# Temporarily disable ESLint during build
RUN if [ -f package.json ]; then mv eslint.config.mjs eslint.config.mjs.bak 2>/dev/null || true; fi
RUN if [ -f package.json ]; then npm run build; fi

# Main Python application stage
FROM python:3.11-slim

# Build arguments
ARG BUILD_ENV=production
ARG PUID=1000
ARG PGID=1000

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH="/app:/app/api" \
    BUILD_ENV=${BUILD_ENV}

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    libpq-dev \
    curl \
    wget \
    ca-certificates \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Create application user and group
RUN groupadd -r -g ${PGID} aphrodite && \
    useradd -r -u ${PUID} -g aphrodite -s /bin/bash -d /app aphrodite

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY api/requirements.txt ./api/
RUN pip install --upgrade pip && \
    pip install -r api/requirements.txt

# Copy application code
COPY . .

# Copy frontend build from previous stage (ensure directories exist first)
RUN mkdir -p ./frontend/.next ./frontend/
COPY --from=frontend-builder /frontend-build/.next ./frontend/.next/
COPY --from=frontend-builder /frontend-build/package*.json ./frontend/

# Create necessary directories with correct permissions
RUN mkdir -p \
    /app/api/static/processed \
    /app/api/cache/posters \
    /app/media \
    /app/logs \
    /app/temp \
    /app/config \
    /app/cache \
    /app/images \
    && chown -R aphrodite:aphrodite /app \
    && chmod -R 755 /app

# Copy and set up entrypoint script
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Expose ports
EXPOSE 8000 3000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["api"]
