FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies including Node.js for frontend build
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
COPY aphrodite-web/requirements.txt ./web-requirements.txt

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install -r web-requirements.txt

# Copy frontend files first to build separately
COPY aphrodite-web/frontend /app/aphrodite-web/frontend

# Build the frontend
WORKDIR /app/aphrodite-web/frontend
RUN npm install && npm run build

# Return to app directory
WORKDIR /app

# Copy config processor script
COPY config_from_env.py /app/

# Copy application code
COPY . .

# Create necessary directories with correct permissions
RUN mkdir -p /app/posters/original /app/posters/working /app/posters/modified /app/data && \
    chmod -R 775 /app/posters /app/data

# Create a non-root user and set permissions
RUN groupadd -r aphrodite && \
    useradd -r -g aphrodite -s /bin/bash -d /app aphrodite && \
    chown -R aphrodite:aphrodite /app && \
    # Make config files writable by the aphrodite user
    chmod 664 /app/settings.yaml /app/badge_settings_*.yml 2>/dev/null || true

# Switch to non-root user
USER aphrodite

# Set up entrypoint script
COPY --chown=aphrodite:aphrodite entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the default Flask port
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command - can be overridden with environment variables
CMD ["web"]