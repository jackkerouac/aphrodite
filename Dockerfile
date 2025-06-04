FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Install system dependencies including Node.js for frontend build and gosu for user switching
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

# Ensure complete settings file is present
COPY settings.yaml /app/settings.yaml

# Ensure template files are present for config initialization
COPY settings.yaml.template /app/settings.yaml.template

# Create necessary directories with correct permissions
RUN mkdir -p /app/posters/original /app/posters/working /app/posters/modified /app/data /app/config && \
    chmod -R 775 /app/posters /app/data /app/config

# Create a default user and group (will be modified at runtime if PUID/PGID specified)
RUN groupadd -r -g 1000 aphrodite && \
    useradd -r -u 1000 -g aphrodite -s /bin/bash -d /app aphrodite && \
    chown -R aphrodite:aphrodite /app

# Set default PUID and PGID
ENV PUID=1000 PGID=1000

# Set up entrypoint script (copy as root, will be owned by correct user after runtime user setup)
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Expose the default Flask port
EXPOSE 5000

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Default command - can be overridden with environment variables
CMD ["web"]