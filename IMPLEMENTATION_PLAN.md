# Aphrodite UI - API Settings Implementation Plan

This document outlines the phased implementation plan for the API Settings module in Aphrodite UI.

## Current State

- Basic UI structure with sidebar navigation
- Jellyfin API integration working
- Database schema for all API integrations
- Backend endpoints for all API integrations
- Working UI for API Settings
- Partially working UI for Resolution Badge Settings

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
- ✅ Implement OMDB API settings UI card
- ✅ Connect UI to backend endpoints
- ✅ Test API key storage and retrieval
- ✅ Implement connection testing for OMDB API
- ✅ Add error handling and visual feedback

### 2.3 TMDB API Integration
- ✅ Implement TMDB API settings UI card
- ✅ Connect UI to backend endpoints
- ✅ Test API key storage and retrieval
- ✅ Implement connection testing for TMDB API
- ✅ Add error handling and visual feedback

### 2.4 aniDB API Integration
- ✅ Implement aniDB API settings UI card
- ✅ Connect UI to backend endpoints
- ✅ Test API key and PIN storage and retrieval
- ✅ Implement connection testing for aniDB API
- ✅ Add error handling and visual feedback

### 2.5 Integration Testing
- ✅ Test all API integrations together
- ✅ Ensure proper responsive layout
- ✅ Verify database persistence for all settings
- ✅ Test error handling scenarios

## Phase 3: Dashboard Implementation

- ✅ Create dashboard layout with card components
- ⬜ Implement statistics widgets
- ⬜ Add recent activity feed
- ⬜ Create system status indicators
- ⬜ Implement library statistics charts

## Phase 4: Run Configuration

- ⬜ Build job configuration interface
- ⬜ Implement library selection using connected APIs
- ⬜ Create poster style options panel
- ⬜ Add run preview capability

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