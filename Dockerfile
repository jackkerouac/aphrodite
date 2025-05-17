# Build stage for the Vue frontend
FROM node:16-alpine AS frontend-builder
WORKDIR /app
COPY aphrodite-web/frontend/package*.json ./
RUN npm install
COPY aphrodite-web/frontend/ ./
RUN npm run build

# Final image
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies for image processing and debugging
RUN apt-get update && apt-get install -y \
    libmagic1 \
    libpng-dev \
    libjpeg-dev \
    procps \
    vim \
    && rm -rf /var/lib/apt/lists/*

# Create necessary directories with very permissive permissions for debugging
RUN mkdir -p posters/original posters/working posters/modified data/config app/static && \
    chmod -R 777 posters data app/static

# Copy the Python application
COPY aphrodite.py .
COPY aphrodite_helpers/ ./aphrodite_helpers/

# Copy default configuration files to the default_configs directory
COPY settings.yaml ./default_configs/
COPY badge_settings_*.yml ./default_configs/

# Also copy them to the root for use when not mounted
COPY settings.yaml .
COPY badge_settings_*.yml ./

# Make configuration files fully writable for debugging
RUN chmod 666 *.yaml *.yml default_configs/*.yaml default_configs/*.yml

# Copy the web application (Flask backend)
COPY aphrodite-web/app/ ./app/

# Copy our Docker-specific files
COPY docker-main.py ./main.py
COPY docker-config-service.py ./app/services/config.py
COPY docker-config-api.py ./app/api/config.py
COPY docker-app-init.py ./app/__init__.py

# Install Python dependencies - first core requirements, then web app requirements
COPY requirements.txt core-requirements.txt
COPY aphrodite-web/requirements.txt web-requirements.txt
RUN pip install --no-cache-dir -r core-requirements.txt && \
    pip install --no-cache-dir -r web-requirements.txt && \
    pip install python-magic waitress

# Copy the built frontend from the builder stage
COPY --from=frontend-builder /app/dist/ ./app/static/

# Make everything maximally permissive for debugging
RUN chmod -R 777 /app

# Expose the web interface port
EXPOSE 5000

# Command to run the web application
CMD ["python", "main.py"]
