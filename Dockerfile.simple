# Simplified Dockerfile using pre-built frontend
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

# Install Python dependencies
WORKDIR /app
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variables
ENV PATH="/home/aphrodite/.local/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1 \
    API_HOST=0.0.0.0 \
    API_PORT=8000 \
    ENVIRONMENT=production

# Copy application code
COPY --chown=aphrodite:aphrodite api/ ./api/
COPY --chown=aphrodite:aphrodite shared/ ./shared/
COPY --chown=aphrodite:aphrodite aphrodite_logging/ ./aphrodite_logging/
COPY --chown=aphrodite:aphrodite aphrodite_helpers/ ./aphrodite_helpers/

# Copy pre-built frontend
COPY --chown=aphrodite:aphrodite frontend/.next ./frontend/.next
COPY --chown=aphrodite:aphrodite frontend/public ./frontend/public
COPY --chown=aphrodite:aphrodite frontend/package.json ./frontend/package.json

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
