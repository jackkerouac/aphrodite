# Aphrodite v2 - Modern Media Poster Enhancement System

## 🎯 Overview

Aphrodite v2 is a complete rewrite of the media poster enhancement system using modern architecture and best practices.

## 🏗️ Architecture

- **API**: FastAPI backend with async support
- **Frontend**: Next.js with shadcn/ui components  
- **Workers**: Celery background job processing
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Caching**: Redis for sessions and job queues
- **Logging**: Structured logging from day one

## 🚀 Development Setup

### Prerequisites

- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Git

### Quick Start

1. **Check Environment Status**
   ```bash
   cd aphrodite-v2
   python dev-manager.py status
   ```

2. **Start Development Environment**
   ```bash
   python dev-manager.py start v2
   ```

3. **Access Services**
   - Frontend: http://localhost:3000
   - API Documentation: http://localhost:8000/docs
   - Monitoring: http://localhost:8080

### Parallel Development

You can run both v1 and v2 simultaneously:

```bash
# Start both versions
python dev-manager.py start all

# Check status
python dev-manager.py status

# Stop everything
python dev-manager.py stop all
```

## 📁 Project Structure

```
aphrodite-v2/
├── api/                    # FastAPI backend
├── frontend/              # Next.js frontend
├── workers/               # Celery workers
├── shared/                # Shared utilities
├── migration-tools/       # v1 to v2 migration
├── logging/               # Structured logging
├── monitoring/            # Health checks
├── docs/                  # Documentation
└── dev-manager.py         # Environment manager
```

## 🔍 Logging System

Comprehensive logging is built into every component:

- **Structured Logs**: JSON format for easy parsing
- **Correlation IDs**: Track requests across services
- **Multiple Levels**: Debug, Info, Warning, Error
- **Multiple Outputs**: Console, files, database

## 📊 Development Phases

- **Phase 1**: Foundation & Infrastructure ✅
- **Phase 2**: Core API Development 🚧
- **Phase 3**: Frontend Development 📋
- **Phase 4**: Background Processing 📋
- **Phase 5**: Migration & Deployment 📋

## 🛠️ Development Tools

- `dev-manager.py` - Environment management
- `data-sync.py` - Data synchronization
- `comparison-test.py` - Version comparison
- `log-analyzer.py` - Log analysis

## 📋 Current Status

🚧 **Phase 1: Foundation Setup** - In Progress

- [x] Repository structure created
- [x] Development environment manager
- [x] Logging system foundation
- [ ] Docker configuration
- [ ] Database setup
- [ ] CI/CD pipeline

## 🤝 Contributing

This is an active development project. Please see the master development plan for detailed roadmap and contribution guidelines.
