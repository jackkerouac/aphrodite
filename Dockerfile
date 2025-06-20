# Multi-stage Dockerfile for Aphrodite v4.0.0
# Alternative build approach for Tailwind CSS v4 compatibility

#################################################################
# Stage 1: Frontend Build (with special handling for Tailwind v4)
#################################################################
FROM node:18.20-slim AS frontend-build

# Install build dependencies including extra tools for native compilation
RUN apt-get update && apt-get install -y \
    python3 \
    make \
    g++ \
    libc6-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /frontend

# Copy package files
COPY frontend/package*.json ./

# Install dependencies with verbose logging for debugging
RUN npm ci --include=dev

# Copy frontend source
COPY frontend/ ./

# Set build environment variables
ENV NODE_ENV=production
ENV SKIP_ENV_VALIDATION=1
ENV NEXT_TELEMETRY_DISABLED=1

# Build frontend with simplified approach
RUN echo "🚀 Starting Next.js build..." && \
    npm run build:docker || npm run build

#################################################################
# Stage 2: Python Dependencies
#################################################################
FROM python:3.11-slim AS python-deps

# Install system dependencies for compilation
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    python3-dev \
    build-essential \
    libffi-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install Python dependencies
COPY api/requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

#################################################################
# Stage 3: Production Runtime
#################################################################
FROM python:3.11-slim AS production

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gosu \
    libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r aphrodite \
    && useradd -r -g aphrodite aphrodite

# Copy Python dependencies from build stage
COPY --from=python-deps /root/.local /home/aphrodite/.local

# Set environment variables
ENV PATH="/home/aphrodite/.local/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    ENVIRONMENT=production

WORKDIR /app

# Copy application code
COPY --chown=aphrodite:aphrodite api/ ./api/
COPY --chown=aphrodite:aphrodite shared/ ./shared/
COPY --chown=aphrodite:aphrodite aphrodite_logging/ ./aphrodite_logging/
COPY --chown=aphrodite:aphrodite aphrodite_helpers/ ./aphrodite_helpers/

# Copy built frontend from build stage
COPY --from=frontend-build --chown=aphrodite:aphrodite /frontend/.next ./frontend/.next
COPY --from=frontend-build --chown=aphrodite:aphrodite /frontend/public ./frontend/public
COPY --from=frontend-build --chown=aphrodite:aphrodite /frontend/package.json ./frontend/package.json

# Create necessary directories
RUN mkdir -p /app/logs /app/data /app/media && \
    chown -R aphrodite:aphrodite /app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Expose port
EXPOSE 8000

# Switch to non-root user
USER aphrodite

# Set working directory to API
WORKDIR /app/api

# Start the FastAPI application
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
