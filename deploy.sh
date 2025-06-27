#!/bin/bash
# Aphrodite One-Line Deployment Script

echo "🚀 Deploying Aphrodite..."

# Download deployment files
echo "📥 Downloading configuration files..."
curl -L -o docker-compose.yml https://github.com/jackkerouac/aphrodite/releases/latest/download/docker-compose.yml
curl -L -o .env https://github.com/jackkerouac/aphrodite/releases/latest/download/.env.example

if [ ! -f docker-compose.yml ] || [ ! -f .env ]; then
    echo "❌ Failed to download required files"
    exit 1
fi

echo "✅ Configuration files downloaded"

# Check if user needs to edit .env
if grep -q "your-secure-database-password-here" .env; then
    echo ""
    echo "⚠️  IMPORTANT: You must edit .env before continuing!"
    echo "   - Change POSTGRES_PASSWORD"
    echo "   - Change SECRET_KEY"
    echo ""
    echo "Generate a secure key with: openssl rand -base64 64"
    echo ""
    echo "After editing .env, run: docker compose up -d"
    exit 0
fi

# Start services
echo "🐳 Starting Aphrodite services..."
docker compose up -d

echo ""
echo "🎉 Aphrodite is starting up!"
echo "📍 Visit: http://localhost:8000"
echo "📊 Status: docker compose ps"
echo "📝 Logs: docker compose logs -f"
