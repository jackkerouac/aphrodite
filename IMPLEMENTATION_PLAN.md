# Aphrodite UI - API Settings Implementation Plan

This document outlines the phased implementation plan for the API Settings module in Aphrodite UI.

## Current State

- Basic UI structure with sidebar navigation
- Jellyfin API integration working
- Database schema for all API integrations
- Backend endpoints for all API integrations
- Placeholder UI elements for OMDB, TMDB, and TVDB APIs

## Phase 1: Infrastructure and Jellyfin (Completed)

- ✅ Set up project structure with React, Vite, and Tailwind CSS
- ✅ Create navigation sidebar with routes for all sections
- ✅ Implement Jellyfin API settings UI
- ✅ Create backend endpoints for Jellyfin settings
- ✅ Set up database schema for Jellyfin settings
- ✅ Implement connection testing for Jellyfin API

## Phase 2: Additional API Integrations (Next)

### 2.1 Database and Server Preparation
- ✅ Create database tables for OMDB, TMDB, and TVDB settings
- ✅ Implement backend endpoints for additional APIs
- ✅ Add test user for development purposes
- ✅ Create database setup and testing scripts

### 2.2 OMDB API Integration (Next Step)
- ⬜ Implement OMDB API settings UI card
- ⬜ Connect UI to backend endpoints
- ⬜ Test API key storage and retrieval
- ⬜ Implement connection testing for OMDB API
- ⬜ Add error handling and visual feedback

### 2.3 TMDB API Integration
- ⬜ Implement TMDB API settings UI card
- ⬜ Connect UI to backend endpoints
- ⬜ Test API key storage and retrieval
- ⬜ Implement connection testing for TMDB API
- ⬜ Add error handling and visual feedback

### 2.4 TVDB API Integration
- ⬜ Implement TVDB API settings UI card
- ⬜ Connect UI to backend endpoints
- ⬜ Test API key and PIN storage and retrieval
- ⬜ Implement connection testing for TVDB API
- ⬜ Add error handling and visual feedback

### 2.5 Integration Testing
- ⬜ Test all API integrations together
- ⬜ Ensure proper responsive layout
- ⬜ Verify database persistence for all settings
- ⬜ Test error handling scenarios

## Phase 3: Dashboard Implementation

- ⬜ Create dashboard layout with card components
- ⬜ Implement statistics widgets
- ⬜ Add recent activity feed
- ⬜ Create system status indicators
- ⬜ Implement library statistics charts

## Phase 4: Run Configuration

- ⬜ Build job configuration interface
- ⬜ Implement library selection using connected APIs
- ⬜ Create poster style options panel
- ⬜ Add run preview capability

## Implementation Strategy for API Settings UI

### 1. Implementation Approach for OMDB Integration

1. **Modify the API settings page**
   - Start by enabling only the OMDB API card
   - Keep TMDB and TVDB as placeholder cards
   - Update ApiSettingsCard component to handle the single API key field

2. **Testing Strategy**
   - First verify database schema is correctly set up
   - Test backend endpoints using Postman or curl
   - Implement UI and test saving/retrieving API key
   - Test connection to OMDB API with a valid key

3. **Error Handling**
   - Add validation for the API key field
   - Implement proper error messages for invalid keys
   - Add toast notifications for success/failure

### 2. Implementation Approach for TMDB Integration

Once OMDB integration is complete:

1. **Enable the TMDB card**
   - Update the placeholder card with the actual form
   - Reuse the ApiSettingsCard component
   - Implement similar structure to OMDB

2. **Testing**
   - Test TMDB API connection with a valid key
   - Verify error handling for invalid keys
   - Ensure proper storage in the database

### 3. Implementation Approach for TVDB Integration

After TMDB integration:

1. **Enable the TVDB card**
   - Update the placeholder with the actual form
   - Add both API key and PIN fields
   - Implement proper validation

2. **Testing**
   - Test TVDB API connection with valid credentials
   - Verify error handling
   - Test optional PIN field behavior

## Development Setup

Before beginning implementation:

1. **Verify database setup**
   ```bash
   npm run test-db
   ```

2. **Start backend server**
   ```bash
   npm run server
   ```

3. **Start frontend development server**
   ```bash
   npm run dev
   ```

4. **Test current Jellyfin integration**
   - Enter valid Jellyfin credentials
   - Save settings and verify they persist
   - Test connection to confirm the flow works

## Next Immediate Steps

1. Implement the OMDB API card (replacing the placeholder)
2. Test the OMDB integration thoroughly
3. Once OMDB is working, move on to TMDB
4. Finally implement TVDB integration
5. Test all integrations working together

## Notes and Considerations

- Maintain consistent UI patterns across all API integrations
- Reuse the ApiSettingsCard component for all APIs
- Consider adding a "Reset" button to clear API settings
- Implement proper loading states for all operations
- Ensure all API keys are properly handled as sensitive information
