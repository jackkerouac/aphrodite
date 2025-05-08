# Aphrodite Badge System Refactoring Plan (Updated)

## Overview

This plan outlines the steps to consolidate separate badge settings pages (Audio, Resolution, Review) into a unified Preview page with integrated settings. The system will use a canvas overlay approach with standard poster dimensions (1000px width) and save badges with transparent backgrounds for application to Jellyfin posters.

## Phase 1: Preparation and Analysis (1-2 days)

- [x] **1.1 Audit existing components**
  - [x] Identify all components and code in current badge settings pages
  - [x] Document the data structures and state management for each badge type
  - [x] Catalog reusable components vs. components to be deprecated

- [x] **1.2 Create scaffolding for new features**
  - [x] Set up a feature branch for the refactoring work
  - [x] Create folder structure for new modular components
  - [x] Set up basic unit tests to validate refactoring results

- [x] **1.3 Design the database schema updates**
  - [x] Create migration plans for updating badge tables to include position data
  - [x] Design schema for storing badge positions as percentages of poster dimensions

## Phase 2: Core Badge and Poster Services (2-3 days)

- [x] **2.1 Create poster handling service**
  - [x] Implement poster resizing utility to standardize dimensions (1000px width)
  - [x] Create poster caching mechanism for better performance
  - [x] Add utility to calculate aspect ratios and dimensions

```typescript
// src/services/posterService.ts
export interface PosterDimensions {
  width: number;
  height: number;
  aspectRatio: number;
}

export const resizePoster = (
  originalUrl: string, 
  targetWidth: number = 1000
): Promise<{url: string, dimensions: PosterDimensions}> => {
  // Resize logic here
};

export const calculateBadgePosition = (
  posterDimensions: PosterDimensions,
  badgePosition: {x: number, y: number, percentX?: number, percentY?: number}
): {x: number, y: number, percentX: number, percentY: number} => {
  // Convert between absolute and percentage positions
};
```

- [x] **2.2 Create badge rendering service**
  - [x] Implement canvas-based rendering for each badge type
  - [x] Create utility functions for common canvas operations
  - [x] Add functions to render badges with transparent backgrounds

```typescript
// src/services/badgeRenderer.ts
export interface BadgeRenderingOptions {
  size: number;
  backgroundColor: string;
  backgroundOpacity: number;
  // ... other common properties
}

export const renderBadgeToCanvas = async (
  type: 'audio' | 'resolution' | 'review',
  options: BadgeRenderingOptions, 
  sourceImageUrl?: string
): Promise<HTMLCanvasElement> => {
  // Canvas rendering logic
};

export const extractBadgeWithTransparency = (
  canvas: HTMLCanvasElement,
  badgeBounds: {x: number, y: number, width: number, height: number}
): string => {
  // Extract badge from canvas with transparent background
  // Return as base64 PNG
};
```

- [x] **2.3 Create badge storage service**
  - [x] Implement functions to save transparent badge images
  - [x] Create endpoints for retrieving saved badges
  - [x] Add functions for associating badges with users

- [x] **2.4 Badge settings management hooks**
  - [x] Create unified hook structure for managing all badge types
  - [x] Implement loading & saving functionality
  - [x] Add percentage-based positioning to badge settings

## Phase 3: UI Components Development (3-4 days)

- [x] **3.1 Create consolidated preview component**
  - [x] Implement poster container with standard dimensions
  - [x] Create absolute-positioned canvas overlay
  - [ ] Implement drag-and-drop positioning system

```typescript
// src/components/PosterPreview.tsx
import React, { useEffect, useRef, useState } from 'react';

interface PosterPreviewProps {
  posterUrl: string;
  badges: {
    audio?: BadgeSettings & {position: {percentX: number, percentY: number}};
    resolution?: BadgeSettings & {position: {percentX: number, percentY: number}};
    review?: BadgeSettings & {position: {percentX: number, percentY: number}};
  };
  onBadgePositionChange: (type: string, position: {percentX: number, percentY: number}) => void;
  activeBadgeType: string | null;
}

const PosterPreview: React.FC<PosterPreviewProps> = ({ 
  posterUrl, 
  badges, 
  onBadgePositionChange,
  activeBadgeType 
}) => {
  const posterRef = useRef<HTMLImageElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [posterDimensions, setPosterDimensions] = useState<{width: number, height: number}>({width: 0, height: 0});
  
  // Setup poster and canvas
  useEffect(() => {
    if (posterRef.current) {
      const {width, height} = posterRef.current;
      setPosterDimensions({width, height});
      
      if (canvasRef.current) {
        canvasRef.current.width = width;
        canvasRef.current.height = height;
      }
    }
  }, [posterUrl]);
  
  // Render badges on canvas overlay
  useEffect(() => {
    const renderBadges = async () => {
      if (!canvasRef.current) return;
      
      const ctx = canvasRef.current.getContext('2d');
      if (!ctx) return;
      
      // Clear canvas
      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      
      // Render each badge at its position
      for (const [type, badge] of Object.entries(badges)) {
        if (!badge) continue;
        
        const {percentX, percentY} = badge.position;
        const x = (percentX / 100) * posterDimensions.width;
        const y = (percentY / 100) * posterDimensions.height;
        
        // Render badge at position
        const badgeCanvas = await renderBadgeToCanvas(type as any, badge);
        ctx.drawImage(badgeCanvas, x, y);
      }
    };
    
    renderBadges();
  }, [badges, posterDimensions]);
  
  // Handle drag events for active badge
  const handleDrag = (e: React.DragEvent) => {
    if (!activeBadgeType || !posterDimensions.width) return;
    
    const rect = posterRef.current?.getBoundingClientRect();
    if (!rect) return;
    
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    // Convert to percentages
    const percentX = (x / posterDimensions.width) * 100;
    const percentY = (y / posterDimensions.height) * 100;
    
    onBadgePositionChange(activeBadgeType, {percentX, percentY});
  };
  
  return (
    <div className="relative">
      <img 
        ref={posterRef}
        src={posterUrl} 
        alt="Poster Preview"
        className="w-full h-auto"
      />
      <canvas
        ref={canvasRef}
        className="absolute top-0 left-0 pointer-events-none"
        width={posterDimensions.width}
        height={posterDimensions.height}
      />
      {activeBadgeType && (
        <div 
          className="absolute top-0 left-0 w-full h-full cursor-move"
          onDragOver={(e) => e.preventDefault()}
          onDrop={handleDrag}
        />
      )}
    </div>
  );
};
```

- [x] **3.2 Develop badge settings panels**
  - [x] Create tabbed interface for different badge types
  - [ ] Implement collapsible settings sections
  - [ ] Create reusable controls for common settings

- [x] **3.3 Build badge extraction functionality**
  - [x] Implement canvas-based badge isolation feature
  - [x] Add transparent background handling
  - [ ] Create badge preview with transparency grid

## Phase 4: Backend API Development (2-3 days)

- [ ] **4.1 Implement badge image saving endpoints**
  - [ ] Create route for saving isolated transparent badges
  - [ ] Implement user authentication middleware
  - [ ] Add validation for badge positioning data

```javascript
// src/server/routes/badgeRoutes.js
router.post('/badges/:type', auth, async (req, res) => {
  try {
    const { type } = req.params;
    const { imageData, settings, position } = req.body;
    const userId = req.user.id;
    
    // Validate position is in percentage format
    if (position && (position.percentX === undefined || position.percentY === undefined)) {
      return res.status(400).json({ 
        success: false, 
        message: 'Position must include percentX and percentY values' 
      });
    }
    
    // Save the badge with position data
    const result = await badgeService.saveBadge(userId, type, imageData, {
      ...settings,
      position
    });
    
    res.json({ success: true, data: result });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});
```

- [ ] **4.2 Update badge settings endpoints**
  - [ ] Modify existing routes to handle percentage-based positioning
  - [ ] Add batch update endpoint for all badge types
  - [ ] Create endpoint to get all badge settings for a user

- [ ] **4.3 Implement badge application service**
  - [ ] Create service to apply transparent badges to posters using positions
  - [ ] Add caching mechanism for processed posters
  - [ ] Implement Jellyfin poster integration

## Phase 5: Integration and Optimization (2-3 days)

- [ ] **5.1 Integrate all components**
  - [ ] Connect poster preview to badge rendering service
  - [ ] Link settings panels to badge preview updates
  - [ ] Implement save functionality for all badge types

- [ ] **5.2 Optimize performance**
  - [ ] Add debouncing for canvas re-renders
  - [ ] Implement smart updates to avoid unnecessary re-renders
  - [ ] Add caching for badge renderings

```typescript
// src/hooks/useBadgePreview.ts
export const useBadgePreview = (badgeSettings, debounceMs = 300) => {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isRendering, setIsRendering] = useState(false);
  
  // Use memo to cache expensive badge renders
  const badgeSettingsKey = JSON.stringify(badgeSettings);
  
  const debouncedSettings = useDebounce(badgeSettings, debounceMs);
  
  useEffect(() => {
    const renderPreview = async () => {
      setIsRendering(true);
      try {
        const canvas = await renderBadgeToCanvas(
          debouncedSettings.type,
          debouncedSettings
        );
        
        setPreviewUrl(canvas.toDataURL('image/png'));
      } catch (error) {
        console.error('Error rendering badge preview:', error);
      } finally {
        setIsRendering(false);
      }
    };
    
    renderPreview();
  }, [debouncedSettings]);
  
  return { previewUrl, isRendering };
};
```

- [ ] **5.3 Add advanced features**
  - [ ] Implement badge presets system
  - [ ] Add badge alignment guides (center, edges, etc.)
  - [ ] Create template library for common badge setups

## Phase 6: Testing and Cleanup (2-3 days)

- [ ] **6.1 Comprehensive testing**
  - [ ] Verify all badge types render correctly with transparency
  - [ ] Test positioning system with various poster aspect ratios
  - [ ] Validate settings save/load functionality

- [ ] **6.2 Code cleanup**
  - [ ] Remove deprecated badge settings pages
  - [ ] Clean up unused routes and components
  - [ ] Ensure consistent API interfaces

- [ ] **6.3 Documentation**
  - [ ] Update API documentation
  - [ ] Create user guide for the new badge system
  - [ ] Document architecture for future development

## Phase 7: Docker Integration (1-2 days)

- [ ] **7.1 Update Docker configuration**
  - [ ] Configure volume for badge storage
  - [ ] Update environment variables for file paths
  - [ ] Test badge system in containerized environment

- [ ] **7.2 CI/CD updates**
  - [ ] Update build process for new architecture
  - [ ] Add tests for Docker deployment
  - [ ] Create automated migration scripts

## File Structure

```
src/
├── components/
│   ├── badges/
│   │   ├── BadgeEditor.tsx            # Main badge editing component
│   │   ├── BadgePreview.tsx           # Badge preview with transparency
│   │   ├── BadgePositioner.tsx        # Badge positioning component
│   │   ├── controls/                  # Reusable control components
│   │   │   ├── ColorPicker.tsx
│   │   │   ├── ShadowControls.tsx
│   │   │   └── ...
│   │   └── types/                     # Badge type components
│   │       ├── AudioBadge.tsx
│   │       ├── ResolutionBadge.tsx
│   │       └── ReviewBadge.tsx
│   └── poster/
│       ├── PosterPreview.tsx          # Main poster preview with canvas overlay
│       └── TransparencyGrid.tsx       # Grid background for transparency preview
├── hooks/
│   ├── useBadgeSettings.ts            # Unified hook for badge settings
│   ├── useBadgePreview.ts             # Hook for badge preview rendering
│   ├── usePosterDimensions.ts         # Hook for handling poster dimensions
│   └── useDebounce.ts                 # Debouncing hook for settings
├── pages/
│   ├── Preview.tsx                    # Main consolidated preview page
│   └── ...
├── services/
│   ├── badgeRenderer.ts               # Badge rendering service
│   ├── posterService.ts               # Poster handling service
│   ├── canvasUtils.ts                 # Canvas utility functions
│   └── imageLoader.ts                 # Image loading utilities
└── server/
    ├── controllers/
    │   └── badgeController.js         # Badge endpoints controller
    ├── services/
    │   ├── badgeService.js            # Badge business logic
    │   ├── posterService.js           # Poster processing service
    │   └── imageService.js            # Image handling service
    └── routes/
        └── badgeRoutes.js             # Badge API routes
```

## Dependencies to Add/Consider

- [ ] html2canvas (for badge rendering)
- [ ] react-draggable (for badge positioning)
- [ ] debounce (for performance optimization)
- [ ] uuid (for generating unique filenames)
- [ ] sharp (for server-side image processing)

## Routes to Update

- [ ] GET/POST `/api/audio-badge-settings/:userId` → `/api/badges/audio/:userId`
- [ ] GET/POST `/api/resolution-badge-settings/:userId` → `/api/badges/resolution/:userId`
- [ ] GET/POST `/api/review-badge-settings/:userId` → `/api/badges/review/:userId`
- [ ] POST `/api/upload-audio-badge` → `/api/badges/:type/image`
- [ ] NEW: POST `/api/badges/apply-to-poster`
- [ ] NEW: GET `/api/posters/resize/:jellyfin_id`

## Components to Remove

- [ ] AudioBadgePage.tsx
- [ ] ResolutionBadgePage.tsx
- [ ] ReviewBadgePage.tsx
- [ ] PositionSelector.tsx (to be replaced with drag-and-drop positioning)

## Milestone Timeline

1. **Preparation & Core Services**: Days 1-5
2. **UI Development**: Days 6-10
3. **Backend Integration**: Days 11-13
4. **Testing & Cleanup**: Days 14-16
5. **Docker Integration**: Days 17-18

## Success Criteria

- All badge types configurable from a single Preview page
- Real-time preview of badges on standard-sized poster (1000px width)
- Badge positions stored as percentages for scalability
- Badge images saved with transparent backgrounds
- Modular code structure with maintainable file sizes
- Fully functional in Docker environment