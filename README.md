# Aphrodite UI

A modern UI application for poster generation and media management services, built with React, Vite, and Tailwind CSS.

## Project Overview

Aphrodite UI serves as a frontend for poster generation and management services. The application features a dashboard, run configuration, preview system, job history, logs, scheduler, and settings management.

## Tech Stack

- **Frontend**:
  - React 19.0.0
  - Vite 6.3.1 (Build tool)
  - TypeScript/JavaScript (Currently using JavaScript with TypeScript configurations)
  - Tailwind CSS v4.1.5
  - shadcn/ui components
  - React Router Dom (Routing)
  - Lucide React (Icons)
  - React Query (Data fetching)

- **Backend**:
  - Express.js
  - PostgreSQL database
  - Node.js

## Project Structure

```
/src
  /components      # UI components including shadcn components
  /pages           # Page components for each route
  /lib             # Utility functions and shared code
  /hooks           # Custom React hooks
/backend
  server.js        # Express server with API routes
/db
  /init            # Database initialization scripts
/scripts           # Utility scripts
```

## Features

### Completed
- Initial setup with Vite, React, Tailwind CSS, and shadcn components
- Navigation system with React Router
- Basic UI components including sidebar and layout structure
- Jellyfin API integration with database storage and connection testing

### In Progress
- API Settings expansion
- Dashboard page with statistics
- Theme system with dark/light mode support
- Responsive design for mobile and desktop

## API Settings Module

The API Settings module allows users to configure connections to external media services:

### Current API Integrations
1. **Jellyfin** - Media server connection
   - URL, API key, and user ID configuration
   - Connection testing functionality

### Planned API Integrations (Coming Soon)
1. **OMDB API** - Open Movie Database
2. **TMDB API** - The Movie Database
3. **TVDB API** - TV Database

### Database Structure
Each API has a dedicated table in the PostgreSQL database:
- `jellyfin_settings` - Stores Jellyfin connection details

## Implementation Roadmap

### Phase 1 (Current)
- ✅ Implement Jellyfin API integration
- ⏳ Prepare database schemas for additional API integrations
- ⏳ Implement placeholder UI for upcoming integrations

### Phase 2 (Next)
- Complete OMDB API integration
- Complete TMDB API integration
- Complete TVDB API integration

### Phase 3
- Dashboard page implementation
- Run configuration interface
- Preview system development

## Setup and Development

### Prerequisites
- Node.js 16+
- PostgreSQL 14+

### Installation

1. Clone the repository
```bash
git clone https://github.com/yourusername/aphrodite.git
cd aphrodite
```

2. Install dependencies
```bash
npm install
```

3. Set up database
```bash
# Create PostgreSQL database
createdb aphrodite

# Initialize database schema
node scripts/create-api-tables.js
```

4. Configure environment variables
```bash
# Create .env file
cp .env.example .env

# Edit .env with your database credentials
```

5. Start development servers
```bash
# Start backend server
npm run server

# Start frontend development server
npm run dev
```

## Backend API Endpoints

### Jellyfin Settings
- `GET /api/jellyfin-settings/:userId` - Get Jellyfin settings for a user
- `POST /api/jellyfin-settings/:userId` - Create/update Jellyfin settings
- `POST /api/test-jellyfin-connection` - Test Jellyfin connection

## Troubleshooting

If you encounter any issues with the API settings page:

1. Make sure the database tables are created:
```bash
npm run setup-db
```

2. Check the server logs for any database connection errors

3. Ensure that the correct environment variables are set in your .env file

## License

MIT
