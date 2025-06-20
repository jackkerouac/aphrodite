# === APHRODITE v2 DOCKER BUILD - FIXED VERSION ===
# Build date: 2025-06-19 21:13:15

FROM node:18.20-slim AS frontend-builder

# Install system dependencies for frontend build
RUN apt-get update && apt-get install -y python3 make g++ && rm -rf /var/lib/apt/lists/*

WORKDIR /frontend-build

# Copy package files
COPY frontend/package*.json ./

# CRITICAL: Install ALL dependencies including devDependencies 
# This includes @tailwindcss/postcss which is needed for build
RUN npm ci

# Copy all frontend source code
COPY frontend/ ./

# CRITICAL: Disable ESLint during Docker build
RUN rm -f eslint.config.mjs || true

# Build the frontend
RUN npm run build

# === MAIN PYTHON APPLICATION ===
FROM python:3.11-slim

ARG BUILD_ENV=production
ARG PUID=1000
ARG PGID=1000

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

# Create user
RUN groupadd -r -g ${PGID} aphrodite && \
    useradd -r -u ${PUID} -g aphrodite -s /bin/bash -d /app aphrodite

WORKDIR /app

# Install Python dependencies
COPY api/requirements.txt ./api/
RUN pip install --upgrade pip && pip install -r api/requirements.txt

# Copy application code
COPY . .

# Copy frontend build (create directories first)
RUN mkdir -p ./frontend/.next ./frontend/
COPY --from=frontend-builder /frontend-build/.next ./frontend/.next/
COPY --from=frontend-builder /frontend-build/package*.json ./frontend/

# Create directories and set permissions
RUN mkdir -p \
    /app/api/static/processed \
    /app/api/cache/posters \
    /app/media /app/logs /app/temp \
    /app/config /app/cache /app/images \
    && chown -R aphrodite:aphrodite /app \
    && chmod -R 755 /app

# Setup entrypoint
COPY docker/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

EXPOSE 8000 3000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["api"]
