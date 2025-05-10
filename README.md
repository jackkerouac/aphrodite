# Aphrodite

Aphrodite is a web application for managing Jellyfin media server poster overlays with custom visual badges.

## Quick Start

### Prerequisites

- Node.js 18+ and npm
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL (or use the included Docker setup)

### Development Setup

1. Clone the repository
2. Copy `.env.example` to `.env` and configure your settings
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the database:
   ```bash
   docker-compose up -d
   ```
5. Run database setup:
   ```bash
   npm run setup-db
   ```
6. Start development servers:
   ```bash
   # Terminal 1 - Frontend
   npm run dev

   # Terminal 2 - Backend
   cd backend && npm run dev
   ```

The frontend will be available at http://localhost:5173 and the backend API at http://localhost:5000.

### Docker Deployment

For production deployment using Docker:

```bash
# Using Docker Compose
docker-compose -f docker-compose.prod.yml up -d

# For development with hot-reload
docker-compose -f docker-compose.dev.yml up
```

See [DOCKER.md](DOCKER.md) for detailed Docker deployment instructions.

## Features

- Custom badge design interface
- Live preview of poster overlays
- Batch processing of media libraries
- Integration with multiple data sources (TMDB, OMDb, Metacritic)
- Job history and logging

## Documentation

- [Docker Deployment Guide](DOCKER.md)
- [Database Setup](DATABASE_SETUP.md)
- [API Endpoints](ENDPOINT.md)
- [Testing Guide](TESTING.md)

## Project Structure

```
/
├── backend/          # Express API backend
├── src/              # React frontend
├── db/               # Database migrations
├── scripts/          # Utility scripts
├── public/           # Static assets
└── tests/            # Test files
```

## Environment Variables

See `.env.example` for all configuration options. Key variables:

- `PG_*` - PostgreSQL connection settings
- `PORT` - Backend server port (default: 5000)
- `FRONTEND_URL` - Frontend URL for CORS

## License

[License information to be added]
