# Optimized Implementation Prompt for Run Aphrodite

## Project Context
You are working on the Aphrodite project, a Jellyfin media server enhancement tool. The project is located at `E:\programming\aphrodite`. You have access to the filesystem and database through MCP.

## Current Task
Continue implementation of the Run Aphrodite feature - Phase 3, Step 8: WebSocket Infrastructure.
**NEW**: Set up WebSocket server for real-time job status updates and create client-side connection handler.

## Project Structure Overview
```
E:\programming\aphrodite/
├── src/                      # Frontend source code
│   ├── pages/               # Page components
│   │   ├── run-aphrodite.tsx (✓ Updated with job creation)
│   │   ├── preview.tsx
│   │   ├── test-library-items.tsx
│   │   ├── test-integration.tsx
│   │   ├── test-jobs.tsx (✓ Created)
│   │   └── settings/
│   ├── components/          # Reusable components
│   │   ├── library-selector.tsx (✓ Completed)
│   │   ├── user-selector.tsx (✓ Completed)
│   │   ├── poster-selector.tsx (✓ Completed)
│   │   ├── poster-grid.tsx (✓ Completed)
│   │   └── error-boundary.tsx (✓ Completed)
│   ├── hooks/              # Custom React hooks
│   │   ├── useEnabledBadges.ts (✓ Completed)
│   │   ├── useJellyfinLibraries.ts (✓ Completed)
│   │   ├── useLibraryItems.ts (✓ Completed)
│   │   └── useCreateJob.ts (✓ Created)
│   ├── contexts/           # React contexts
│   │   └── UserContext.tsx (✓ Completed)
│   ├── lib/                # Utilities and API
│   │   ├── api-client.ts (✓ Updated with jobs API)
│   │   └── api/           # API modules
│   │       ├── audio-badge.ts
│   │       ├── resolution-badge.ts
│   │       ├── review-badge.ts
│   │       ├── jellyfin.ts
│   │       ├── library-items.ts (✓ Created)
│   │       └── jobs.ts (✓ Created)
│   └── App.jsx            # Main app with routing & React Query
├── backend/                # Express backend
│   ├── routes/            # API routes
│   │   ├── audioBadgeSettingsRoutes.js
│   │   ├── resolutionBadgeSettingsRoutes.js
│   │   ├── reviewBadgeSettingsRoutes.js
│   │   ├── jellyfinLibraries