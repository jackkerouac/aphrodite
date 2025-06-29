# Contributing to Aphrodite

Welcome to Aphrodite! This guide will help you set up a local development environment and contribute to the project.

## Quick Start

Get up and running in under 5 minutes:

### For Windows/PowerShell Users (VS Code)
```powershell
# 1. Clone the repository
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite

# 2. Run development setup script
.\scripts\dev-setup.ps1

# 3. Start development environment
docker-compose -f docker-compose.dev.yml up -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

### For Linux/macOS Users
```bash
# 1. Clone the repository
git clone https://github.com/jackkerouac/aphrodite.git
cd aphrodite

# 2. Make scripts executable and run setup
chmod +x scripts/*.sh
./scripts/dev-setup.sh

# 3. Start development environment
docker-compose -f docker-compose.dev.yml up -d

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Documentation: http://localhost:8000/docs
```

## Prerequisites

- **Docker Desktop** - For containerized development (required)
- **Git** - For version control
- **PowerShell 5.1+** - For Windows users (VS Code terminal)
- **Bash** - For Linux/macOS users
- **Node.js 18+** - For frontend development (optional, if running natively)
- **Python 3.11+** - For backend development (optional, if running natively)

## Development Setup Options

### Option 1: Docker Development (Recommended)

This is the easiest way to get started and ensures consistency across all platforms.

#### Windows/PowerShell:
```powershell
# Start all services with hot reloading
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Rebuild after dependency changes
docker-compose -f docker-compose.dev.yml up --build
```

#### Linux/macOS:
```bash
# Start all services with hot reloading
docker-compose -f docker-compose.dev.yml up -d

# View logs
docker-compose -f docker-compose.dev.yml logs -f

# Stop services
docker-compose -f docker-compose.dev.yml down

# Rebuild after dependency changes
docker-compose -f docker-compose.dev.yml up --build
```

**Services:**
- **Frontend**: http://localhost:3000 (Next.js with hot reloading)
- **Backend API**: http://localhost:8000 (FastAPI with hot reloading)
- **API Docs**: http://localhost:8000/docs (Swagger UI)
- **Database**: PostgreSQL on port 5433
- **Redis**: Redis on port 6379

### Option 2: Hybrid Development

Run database services in Docker but frontend/backend natively for maximum development speed.

#### Windows/PowerShell:
```powershell
# Start only database services
docker-compose -f docker-compose.dev.yml up postgres redis -d

# Run backend natively (PowerShell terminal 1)
cd api
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run frontend natively (PowerShell terminal 2)
cd frontend
npm install
npm run dev
```

#### Linux/macOS:
```bash
# Start only database services
docker-compose -f docker-compose.dev.yml up postgres redis -d

# Run backend natively (terminal 1)
cd api
pip install -r requirements.txt
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Run frontend natively (terminal 2)
cd frontend
npm install
npm run dev
```

## Project Structure

```
aphrodite/
├── api/                    # FastAPI backend
│   ├── main.py            # API entry point
│   ├── requirements.txt   # Python dependencies
│   └── ...
├── frontend/              # Next.js frontend (React + TypeScript)
│   ├── src/               # Source code
│   ├── package.json       # Node.js dependencies
│   └── ...
├── shared/               # Shared utilities between frontend/backend
├── aphrodite_logging/    # Logging utilities
├── aphrodite_helpers/    # Helper functions
├── workers/              # Background job workers
├── scripts/              # Development and deployment scripts
├── docker-compose.dev.yml # Development environment
└── docker-compose.yml    # Production environment
```

## Important: Frontend Build Requirements

⚠️ **Tailwind CSS v4 Notice**: This project uses **Tailwind CSS v4**, which requires the frontend to be built locally before Docker deployment. This is crucial for GitHub Actions and production builds.

#### Windows/PowerShell:
```powershell
# Always build frontend before creating production Docker images
cd frontend
npm run build

# This generates the required .next directory for production
```

#### Linux/macOS:
```bash
# Always build frontend before creating production Docker images
cd frontend
npm run build

# This generates the required .next directory for production
```

## Code Style Guidelines

### Python (Backend)
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Use async/await for database operations
- Maximum line length: 88 characters (Black formatter)

```python
# Good
async def get_user(user_id: int) -> Optional[User]:
    """Retrieve user by ID."""
    return await User.get_or_none(id=user_id)
```

### TypeScript/React (Frontend)
- Use TypeScript for all new code
- Follow React functional components with hooks
- Use Tailwind CSS v4 for styling
- Prefer named exports over default exports

```typescript
// Good
export const UserProfile: React.FC<UserProfileProps> = ({ userId }) => {
  const [user, setUser] = useState<User | null>(null);
  
  return (
    <div className="p-4 bg-white rounded-lg">
      {user?.name}
    </div>
  );
};
```

## Development Workflow

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Code changes are automatically reloaded in development
   - Backend changes trigger FastAPI auto-reload
   - Frontend changes trigger Next.js hot module replacement

3. **Test your changes**

   #### Windows/PowerShell:
   ```powershell
   # Run all tests
   .\scripts\test.ps1

   # Run only backend tests
   .\scripts\test.ps1 -Backend

   # Run only frontend tests
   .\scripts\test.ps1 -Frontend

   # Run only integration tests
   .\scripts\test.ps1 -Integration
   ```

   #### Linux/macOS:
   ```bash
   # Run all tests
   ./scripts/test.sh

   # Run backend tests
   cd api && python -m pytest

   # Run frontend tests
   cd frontend && npm test

   # Run integration tests
   ./scripts/integration-test.sh
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add user profile component"
   git push origin feature/your-feature-name
   ```

### Environment Variables

Development environment variables are in `.env.development`. Copy and modify as needed:

#### Windows/PowerShell:
```powershell
Copy-Item .env.development .env.local
# Edit .env.local with your specific settings
```

#### Linux/macOS:
```bash
cp .env.development .env.local
# Edit .env.local with your specific settings
```

**Key variables:**
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string  
- `JELLYFIN_URL`: Your Jellyfin server URL
- `DEBUG`: Enable debug logging
- `SECRET_KEY`: JWT secret (change in production)

## Database Development

### Migrations

#### Windows/PowerShell:
```powershell
# Run migrations
cd api
python database_defaults_init.py

# Reset development database
.\scripts\reset-db.ps1
```

#### Linux/macOS:
```bash
# Run migrations
cd api
python database_defaults_init.py

# Reset development database
./scripts/reset-db.sh
```

### Sample Data

The development environment starts with a clean database. Use the web interface to:
1. Configure Jellyfin connection
2. Import your anime library
3. Set up user preferences

## Testing

### Running Tests

#### Windows/PowerShell:
```powershell
# All tests
.\scripts\test.ps1

# Backend only
.\scripts\test.ps1 -Backend

# Frontend only  
.\scripts\test.ps1 -Frontend

# Integration tests
.\scripts\test.ps1 -Integration
```

#### Linux/macOS:
```bash
# All tests
./scripts/test.sh

# Backend only
cd api && python -m pytest

# Frontend only  
cd frontend && npm test

# Integration tests
./scripts/integration-test.sh
```

### Writing Tests

- **Backend**: Use pytest with async support
- **Frontend**: Use Jest and React Testing Library
- **Integration**: Test API endpoints with real database

## Debugging

### Backend Debugging
- Logs available at `http://localhost:8000/logs` or `docker-compose logs api`
- Use debugger: Add `import pdb; pdb.set_trace()` 
- Database queries logged in debug mode

### Frontend Debugging
- React DevTools browser extension
- Console logs available in browser
- Next.js build errors shown in terminal

### Common Issues

**Database connection errors:**

#### Windows/PowerShell:
```powershell
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# Reset database
.\scripts\reset-db.ps1
```

#### Linux/macOS:
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.dev.yml ps postgres

# Reset database
./scripts/reset-db.sh
```

**Frontend build errors with Tailwind v4:**

#### Windows/PowerShell:
```powershell
cd frontend
Remove-Item -Recurse -Force .next, node_modules
npm install
npm run build
```

#### Linux/macOS:
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

**Hot reloading not working:**
```bash
# Restart development services
docker-compose -f docker-compose.dev.yml restart api frontend
```

## Pull Request Process

1. **Before submitting:**
   - [ ] Code follows style guidelines
   - [ ] Tests pass locally
   - [ ] Frontend builds successfully (required for Tailwind v4)
   - [ ] Documentation updated if needed

2. **PR Requirements:**
   - Clear description of changes
   - Link to related issue (if applicable)
   - Screenshots for UI changes
   - Test coverage for new features

3. **Review Process:**
   - Maintainer will review within 48 hours
   - Address feedback promptly
   - Squash commits before merge

## Issue Guidelines

### Reporting Bugs

Use the bug report template and include:
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Docker version, PowerShell/Bash version, etc.)
- Relevant logs or screenshots

### Feature Requests

Use the feature request template and include:
- Use case description
- Proposed solution
- Alternative solutions considered
- Mockups or examples (if applicable)

## Getting Help

- **Documentation**: Check the `/docs` directory
- **Discussions**: GitHub Discussions for questions
- **Issues**: GitHub Issues for bugs and features
- **Development Chat**: Join our Discord (link in README)

## Development Scripts

Both PowerShell (.ps1) and Bash (.sh) versions are provided for cross-platform compatibility.

#### Windows/PowerShell Users:
```powershell
# Setup development environment
.\scripts\dev-setup.ps1

# Run all tests
.\scripts\test.ps1

# Reset development database  
.\scripts\reset-db.ps1

# Build for production (includes frontend)
.\scripts\build.ps1

# Clean development environment
.\scripts\clean.ps1

# Validate setup
.\scripts\validate-setup.ps1
```

#### Linux/macOS Users:
```bash
# Make scripts executable first
chmod +x scripts/*.sh

# Setup development environment
./scripts/dev-setup.sh

# Run all tests
./scripts/test.sh

# Reset development database  
./scripts/reset-db.sh

# Build for production (includes frontend)
./scripts/build.sh

# Clean development environment
./scripts/clean.sh

# Validate setup
./scripts/validate-setup.sh
```

## Performance Considerations

### Backend
- Use async database operations
- Implement proper caching with Redis
- Monitor API response times
- Use database indexes for queries

### Frontend  
- Optimize images and assets
- Use React.memo for expensive components
- Implement proper loading states
- Minimize bundle size

---

Thank you for contributing to Aphrodite! 🚀

For questions or help, open a GitHub Discussion or reach out to the maintainers.
