-- Migration: Create Unified Badge Settings Table

-- Create the table if it doesn't exist
CREATE TABLE IF NOT EXISTS unified_badge_settings (
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
    -- For audio: codec_type
    -- For resolution: resolution_type
    -- For review: review sources, etc.
    properties JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(user_id, badge_type)
);

-- Create index for faster lookups by user_id
CREATE INDEX IF NOT EXISTS unified_badge_settings_user_id_idx ON unified_badge_settings(user_id);
CREATE INDEX IF NOT EXISTS unified_badge_settings_badge_type_idx ON unified_badge_settings(badge_type);

-- Create a trigger function to update the updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_unified_badge_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop the trigger if it exists
DROP TRIGGER IF EXISTS update_unified_badge_settings_updated_at_trigger ON unified_badge_settings;

-- Create the trigger
CREATE TRIGGER update_unified_badge_settings_updated_at_trigger
BEFORE UPDATE ON unified_badge_settings
FOR EACH ROW
EXECUTE FUNCTION update_unified_badge_settings_updated_at();

-- Insert default settings for each badge type for user ID 1 if not already present
-- Audio Badge Default
INSERT INTO unified_badge_settings (
    user_id, 
    badge_type, 
    badge_size, 
    edge_padding, 
    badge_position, 
    background_color, 
    background_opacity, 
    border_size, 
    border_color, 
    border_opacity, 
    border_radius, 
    border_width, 
    shadow_enabled, 
    shadow_color, 
    shadow_blur, 
    shadow_offset_x, 
    shadow_offset_y,
    properties
) 
SELECT 
    1, 
    'audio', 
    100, 
    10, 
    'top-left', 
    '#000000', 
    80, 
    2, 
    '#FFFFFF', 
    80, 
    5, 
    1, 
    false, 
    '#000000', 
    10, 
    0, 
    0,
    '{"codec_type": "dolby_atmos"}'
WHERE NOT EXISTS (
    SELECT 1 FROM unified_badge_settings WHERE user_id = 1 AND badge_type = 'audio'
);

-- Resolution Badge Default
INSERT INTO unified_badge_settings (
    user_id, 
    badge_type, 
    badge_size, 
    edge_padding, 
    badge_position, 
    background_color, 
    background_opacity, 
    border_size, 
    border_color, 
    border_opacity, 
    border_radius, 
    border_width, 
    shadow_enabled, 
    shadow_color, 
    shadow_blur, 
    shadow_offset_x, 
    shadow_offset_y,
    properties
) 
SELECT 
    1, 
    'resolution', 
    100, 
    10, 
    'top-right', 
    '#000000', 
    80, 
    2, 
    '#FFFFFF', 
    80, 
    5, 
    1, 
    false, 
    '#000000', 
    10, 
    0, 
    0,
    '{"resolution_type": "4k"}'
WHERE NOT EXISTS (
    SELECT 1 FROM unified_badge_settings WHERE user_id = 1 AND badge_type = 'resolution'
);

-- Review Badge Default
INSERT INTO unified_badge_settings (
    user_id, 
    badge_type, 
    badge_size, 
    edge_padding, 
    badge_position, 
    display_format,
    background_color, 
    background_opacity, 
    border_size, 
    border_color, 
    border_opacity, 
    border_radius, 
    border_width, 
    shadow_enabled, 
    shadow_color, 
    shadow_blur, 
    shadow_offset_x, 
    shadow_offset_y,
    properties
) 
SELECT 
    1, 
    'review', 
    100, 
    10, 
    'bottom-left', 
    'horizontal',
    '#000000', 
    80, 
    2, 
    '#FFFFFF', 
    80, 
    5, 
    1, 
    false, 
    '#000000', 
    10, 
    0, 
    0,
    '{"review_sources": ["imdb", "rotten_tomatoes"]}'
WHERE NOT EXISTS (
    SELECT 1 FROM unified_badge_settings WHERE user_id = 1 AND badge_type = 'review'
);

-- Add comment to the table
COMMENT ON TABLE unified_badge_settings IS 'Unified table for all badge settings (audio, resolution, review) to ensure consistency';
