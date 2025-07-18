# Multi-stage Dockerfile with ARM64 build support
FROM python:3.11-slim AS production

# Install runtime dependencies and fonts
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gosu \
    libpq5 \
    postgresql-client \
    fonts-dejavu-core \
    fonts-liberation \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd -r aphrodite \
    && useradd -r -g aphrodite aphrodite

# Install Python dependencies
WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Python dependencies
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    ENVIRONMENT=production \
    APHRODITE_ROOT=/app \
    APHRODITE_API_DIR=/app/api \
    APHRODITE_ASSETS_DIR=/app/assets \
    APHRODITE_DATA_DIR=/app/data

# Copy application code
COPY --chown=aphrodite:aphrodite VERSION ./
COPY --chown=aphrodite:aphrodite api/ ./api/
COPY --chown=aphrodite:aphrodite shared/ ./shared/
COPY --chown=aphrodite:aphrodite aphrodite_logging/ ./aphrodite_logging/
COPY --chown=aphrodite:aphrodite aphrodite_helpers/ ./aphrodite_helpers/
COPY --chown=aphrodite:aphrodite init-badge-settings-production.py ./
COPY --chown=root:root docker-entrypoint.sh /docker-entrypoint.sh

# Copy frontend files (pre-built .next directory should exist in repo)
COPY --chown=aphrodite:aphrodite frontend/.next ./frontend/.next
COPY --chown=aphrodite:aphrodite frontend/public ./frontend/public
COPY --chown=aphrodite:aphrodite frontend/package.json ./frontend/package.json

# Create necessary directories with proper permissions
RUN mkdir -p /app/logs /app/data /app/media /app/assets /app/assets/fonts /app/assets/images \
             /app/api/static /app/api/static/preview /app/api/static/processed /app/api/static/originals \
             /app/api/static/awards /app/api/static/awards/black /app/api/static/awards/white \
             /app/frontend/.next && \
    chown -R aphrodite:aphrodite /app && \
    chmod -R 755 /app/api/static

# Copy fonts and assets
COPY --chown=aphrodite:aphrodite fonts/ ./assets/fonts/
COPY --chown=aphrodite:aphrodite images/ ./assets/images/

# Create symlink for backward compatibility with /app/fonts paths in database
RUN ln -sf /app/assets/fonts /app/fonts && \
    ln -sf /app/assets/images /app/images

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/live || exit 1

# Expose port
EXPOSE 8000

# Make entrypoint script executable
RUN chmod +x /docker-entrypoint.sh

# Set working directory to API
WORKDIR /app/api

# Use entrypoint script
ENTRYPOINT ["/docker-entrypoint.sh"]

# Start the FastAPI application directly
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
