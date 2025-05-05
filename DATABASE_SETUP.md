# Database Setup Guide for Aphrodite UI

This guide explains how to set up the PostgreSQL database for the Aphrodite UI application.

## Prerequisites

- PostgreSQL 14 or higher installed and running
- Node.js 16 or higher installed

## Database Structure

Aphrodite uses a PostgreSQL database with the following tables:

1. **users** - Stores user information
   - id (primary key)
   - username
   - email
   - password_hash
   - created_at
   - updated_at

2. **jellyfin_settings** - Stores Jellyfin API settings
   - id (primary key)
   - user_id (foreign key to users.id)
   - jellyfin_url
   - jellyfin_api_key
   - jellyfin_user_id
   - created_at
   - updated_at

3. **omdb_settings** - Stores OMDB API settings
   - id (primary key)
   - user_id (foreign key to users.id)
   - api_key
   - created_at
   - updated_at

4. **tmdb_settings** - Stores TMDB API settings
   - id (primary key)
   - user_id (foreign key to users.id)
   - api_key
   - created_at
   - updated_at

5. **tvdb_settings** - Stores TVDB API settings
   - id (primary key)
   - user_id (foreign key to users.id)
   - api_key
   - pin (optional)
   - created_at
   - updated_at

## Setup Instructions

### 1. Create the PostgreSQL Database

```bash
# Connect to PostgreSQL (you may need to provide your PostgreSQL username)
psql -U postgres

# Create the database
CREATE DATABASE aphrodite;

# Create a user for the application (optional but recommended)
CREATE USER aphrodite WITH ENCRYPTED PASSWORD 'aphrodite_secure_password';

# Grant privileges to the user
GRANT ALL PRIVILEGES ON DATABASE aphrodite TO aphrodite;

# Exit psql
\q
```

### 2. Configure Environment Variables

Create a `.env` file in the project root with your database connection details:

```
# Server port
PORT=5000

# PostgreSQL Database Configuration
PG_USER=aphrodite
PG_HOST=localhost
PG_DATABASE=aphrodite
PG_PASSWORD=aphrodite_secure_password
PG_PORT=5432

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:5173
```

### 3. Run the Database Setup Script

The project includes a script to create all necessary tables:

```bash
# Install dependencies if you haven't already
npm install

# Run the database setup script
npm run setup-db
```

### 4. Verify Setup

You can verify that the tables have been created correctly by connecting to the database:

```bash
# Connect to the aphrodite database
psql -U aphrodite -d aphrodite

# List all tables
\dt

# Check the structure of a specific table
\d jellyfin_settings

# Exit psql
\q
```

## Troubleshooting

### Connection Issues

If you encounter connection issues:

1. Make sure PostgreSQL is running:
   ```bash
   sudo systemctl status postgresql
   ```

2. Check that your database exists:
   ```bash
   psql -U postgres -c "SELECT datname FROM pg_database WHERE datname='aphrodite';"
   ```

3. Verify your user has proper permissions:
   ```bash
   psql -U postgres -c "SELECT usename, usecreatedb, usesuper FROM pg_user WHERE usename='aphrodite';"
   ```

### Table Creation Issues

If the setup script fails to create tables:

1. Check the error message in the console

2. Verify your `.env` file has the correct database credentials

3. Try running the SQL commands manually:
   ```bash
   psql -U aphrodite -d aphrodite -f db/init/01-schema.sql
   ```

## Manual SQL Commands

If you need to create the tables manually, you can use these SQL commands:

```sql
-- Create users table
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create update_modified_column function
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = now();
   RETURN NEW;
END;
$$ language 'plpgsql';

-- Create jellyfin_settings table
CREATE TABLE jellyfin_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    jellyfin_url VARCHAR(255) NOT NULL,
    jellyfin_api_key VARCHAR(255) NOT NULL,
    jellyfin_user_id VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create omdb_settings table
CREATE TABLE omdb_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create tmdb_settings table
CREATE TABLE tmdb_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create tvdb_settings table
CREATE TABLE tvdb_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    api_key VARCHAR(255) NOT NULL,
    pin VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- Create triggers for timestamp updates
CREATE TRIGGER update_users_modtime
BEFORE UPDATE ON users
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_jellyfin_settings_modtime
BEFORE UPDATE ON jellyfin_settings
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_omdb_settings_modtime
BEFORE UPDATE ON omdb_settings
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_tmdb_settings_modtime
BEFORE UPDATE ON tmdb_settings
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

CREATE TRIGGER update_tvdb_settings_modtime
BEFORE UPDATE ON tvdb_settings
FOR EACH ROW EXECUTE FUNCTION update_modified_column();

-- Insert a test user for development
INSERT INTO users (id, username, email, password_hash) 
VALUES (1, 'testuser', 'test@example.com', 'hashed_password') 
ON CONFLICT (id) DO NOTHING;
```

## Database Maintenance

### Backup Database

To backup your Aphrodite database:

```bash
pg_dump -U aphrodite -d aphrodite > aphrodite_backup.sql
```

### Restore Database

To restore from a backup:

```bash
psql -U aphrodite -d aphrodite < aphrodite_backup.sql
```

### Reset Database

If you need to reset the database during development:

```bash
# Connect to PostgreSQL
psql -U postgres

# Drop and recreate the database
DROP DATABASE aphrodite;
CREATE DATABASE aphrodite;
GRANT ALL PRIVILEGES ON DATABASE aphrodite TO aphrodite;

# Exit psql
\q

# Run the setup script again
npm run setup-db
```

## Next Steps

Once your database is set up, you can:

1. Start the backend server: `npm run server`
2. Start the frontend development server: `npm run dev`
3. Access the application at: http://localhost:5173
