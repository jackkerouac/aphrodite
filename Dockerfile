FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH="/app:/app/api"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libffi-dev \
    curl \
    nodejs \
    npm \
    gosu \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories with correct permissions
RUN mkdir -p /app/api/static/processed \
             /app/api/cache/posters \
             /app/media \
             /app/logs \
             /app/temp && \
    chmod -R 775 /app/api/static \
                  /app/api/cache \
                  /app/media \
                  /app/logs \
                  /app/temp

# Build frontend if it exists
RUN if [ -d "/app/frontend" ]; then \
        cd /app/frontend && \
        npm install && \
        npm run build; \
    fi

# Create a default user and group
RUN groupadd -r -g 1000 aphrodite && \
    useradd -r -u 1000 -g aphrodite -s /bin/bash -d /app aphrodite && \
    chown -R aphrodite:aphrodite /app

# Set default PUID and PGID
ENV PUID=1000 PGID=1000

# Copy and set up entrypoint script
COPY entrypoint_v2.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose ports for API and frontend
EXPOSE 8000 3000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command
CMD ["api"]
