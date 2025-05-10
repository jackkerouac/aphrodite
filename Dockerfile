# Multi-stage Dockerfile for Aphrodite

# Stage 1: Build Frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy frontend package files
COPY package*.json ./
COPY tsconfig*.json ./
COPY vite.config.* ./
COPY tailwind.config.js ./
COPY components.json ./
COPY index.html ./

# Install dependencies
RUN npm ci

# Copy frontend source
COPY src ./src
COPY public ./public

# Build frontend
RUN npm run build

# Stage 2: Build Backend and Final Image
FROM node:20-alpine

WORKDIR /app

# Install production dependencies only
COPY backend/package*.json ./backend/
RUN cd backend && npm ci --production

# Copy backend source
COPY backend ./backend

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/dist ./dist

# Copy necessary configuration files
COPY scripts ./scripts
COPY current_schema.sql ./

# Create necessary directories
RUN mkdir -p logs data temp

# Set environment variables
ENV NODE_ENV=production
ENV PORT=5000
ENV DOCKER_CONTAINER=true
ENV IS_DOCKER=true
ENV DATA_DIR=/app/data
ENV TEMP_DIR=/app/temp

# Expose ports
EXPOSE 5000

# Start the application
CMD ["node", "backend/server.js"]
