# Unified Badge Settings Schema

## Overview

This document describes the unified badge settings schema implemented as part of the Aphrodite badge system refactoring. The unified schema replaces the previous separate tables for audio, resolution, and review badge settings with a single table that handles all badge types.

## Schema Structure

The `unified_badge_settings` table has the following structure:

```sql
CREATE TABLE unified_badge_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    badge_type VARCHAR(50) NOT NULL, -- 'audio', 'resolution', 'review'
    
    -- General Settings
    badge_size INTEGER DEFAULT 100, -- slider 1-500
    edge_padding INTEGER DEFAULT 10, -- slider 1-50
    badge_position VARCHAR(50) DEFAULT 'top-left', -- buttons for position
    
    -- Badge Type Specific Settings
    -- For review badges only
    display_format VARCHAR(20) DEFAULT 'horizontal', -- dropdown 'horizontal'/'vertical' (review only)
    
    -- Background Settings
    background_color VARCHAR(50) DEFAULT '#000000',
    background_opacity INTEGER DEFAULT 80, -- slider 0-100
    
    -- Border Settings
    border_size INTEGER DEFAULT 2, -- slider 0-10
    border_color VARCHAR(50) DEFAULT '#FFFFFF',
    border_opacity INTEGER DEFAULT 80, -- slider 0-100
    border_radius INTEGER DEFAULT 5, -- slider 0-50
    border_width INTEGER DEFAULT 1, -- slider 0-10
    
    -- Shadow Settings
    shadow_enabled BOOLEAN DEFAULT false, -- toggle
    shadow_color VARCHAR(50) DEFAULT '#000000',
    shadow_blur INTEGER DEFAULT 10, -- slider 0-20
    shadow_offset_x INTEGER DEFAULT 0, -- slider -20 to 20
    shadow_offset_y INTEGER DEFAULT 0, -- slider -20 to 20
    
    -- Type-specific properties (stored as JSON for extensibility)
    properties JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(user_id, badge_type)
);
```

## Badge Types

The system supports three badge types, distinguished by the `badge_type` field:

1. `audio` - For audio codec badges (Dolby Atmos, DTS, etc.)
2. `resolution` - For resolution badges (4K, 1080p, etc.)
3. `review` - For review score badges (IMDb, Rotten Tomatoes, etc.)

## Type-Specific Properties

Badge-specific properties are stored in the `properties` JSONB field to allow for flexibility and extensibility:

### Audio Badge Properties

```json
{
  "codec_type": "dolby_atmos"
}
```

### Resolution Badge Properties

```json
{
  "resolution_type": "4k"
}
```

### Review Badge Properties

```json
{
  "review_sources": ["imdb", "rotten_tomatoes"],
  "score_type": "percentage"
}
```

## Badge Positions

Badge position is specified using one of the following values:

- `top-left`
- `top-center`
- `top-right`
- `middle-left`
- `center`
- `middle-right`
- `bottom-left`
- `bottom-center`
- `bottom-right`

## Migration

A migration script is provided to transfer data from the legacy tables (`audio_badge_settings`, `resolution_badge_settings`, `review_badge_settings`) to the new unified table. The script performs the following steps:

1. Checks if the old tables and the new unified table exist
2. Gets all users with existing badge settings
3. Migrates each user's settings for each badge type
4. Converts legacy values to the new format (e.g., opacity from 0.0-1.0 to 0-100)

## API Endpoints

The following API endpoints are available for interacting with the unified badge settings:

- `GET /api/badge-settings/:userId/:badgeType` - Get settings for a specific badge type
- `GET /api/badge-settings/:userId` - Get all badge settings for a user
- `POST /api/badge-settings/:userId/:badgeType` - Save settings for a specific badge type
- `DELETE /api/badge-settings/:userId/:badgeType` - Delete settings for a specific badge type

## TypeScript Interfaces

TypeScript interfaces are provided for type safety when working with badge settings in the frontend:

- `BaseBadgeSettings` - Common properties for all badge types
- `AudioBadgeSettings` - Audio badge specific interface
- `ResolutionBadgeSettings` - Resolution badge specific interface
- `ReviewBadgeSettings` - Review badge specific interface
- `UnifiedBadgeSettings` - Union type of all badge settings

## Changes From Previous Implementation

The unified schema makes the following improvements:

1. **Consistency** - All badge types use the same field names and structure
2. **Extensibility** - New badge types or properties can be added without schema changes
3. **Simplified API** - A single set of endpoints for all badge types
4. **Type Safety** - TypeScript interfaces ensure correct usage of properties
5. **Improved Validation** - Centralized validation of settings
6. **Cleaner Code** - Reduced duplication in both frontend and backend

## Default Values

Sensible defaults are provided for all settings to ensure a good out-of-the-box experience:

### Common Defaults

- `badge_size`: 100
- `edge_padding`: 10
- `background_color`: '#000000'
- `background_opacity`: 80
- `border_size`: 2
- `border_color`: '#FFFFFF'
- `border_opacity`: 80
- `border_radius`: 5
- `border_width`: 1
- `shadow_enabled`: false
- `shadow_color`: '#000000'
- `shadow_blur`: 10
- `shadow_offset_x`: 0
- `shadow_offset_y`: 0

### Type-Specific Defaults

#### Audio Badge

- `badge_position`: 'top-left'
- `properties.codec_type`: 'dolby_atmos'

#### Resolution Badge

- `badge_position`: 'top-right'
- `properties.resolution_type`: '4k'

#### Review Badge

- `badge_position`: 'bottom-left'
- `display_format`: 'horizontal'
- `properties.review_sources`: ['imdb', 'rotten_tomatoes']
- `properties.score_type`: 'percentage'
