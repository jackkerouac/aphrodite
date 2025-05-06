-- Migration: Create Resolution Badge Settings Table

-- Create the table if it doesn't exist
CREATE TABLE IF NOT EXISTS resolution_badge_settings (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    size REAL DEFAULT 0.1,
    margin REAL DEFAULT 10,
    background_color VARCHAR DEFAULT '#ffffff',
    background_transparency REAL DEFAULT 0.7, 
    border_radius REAL DEFAULT 5,
    border_width REAL DEFAULT 1,
    border_color VARCHAR DEFAULT '#000000',
    border_transparency REAL DEFAULT 0.9,
    shadow_toggle BOOLEAN DEFAULT FALSE,
    shadow_color VARCHAR DEFAULT '#000000',
    shadow_blur_radius REAL DEFAULT 5,
    shadow_offset_x REAL DEFAULT 0,
    shadow_offset_y REAL DEFAULT 0,
    z_index INTEGER DEFAULT 10,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Add a unique constraint for user_id if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint 
        WHERE conname = 'resolution_badge_settings_user_id_unique'
    ) THEN
        ALTER TABLE resolution_badge_settings 
        ADD CONSTRAINT resolution_badge_settings_user_id_unique UNIQUE (user_id);
    END IF;
END$$;

-- Create index for faster lookups by user_id if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_indexes 
        WHERE indexname = 'resolution_badge_settings_user_id_idx'
    ) THEN
        CREATE INDEX resolution_badge_settings_user_id_idx ON resolution_badge_settings(user_id);
    END IF;
END$$;

-- Insert default settings for user ID 1 if not already present
INSERT INTO resolution_badge_settings (
    user_id, size, margin, background_color, background_transparency, 
    border_radius, border_width, border_color, border_transparency,
    shadow_toggle, shadow_color, shadow_blur_radius, shadow_offset_x,
    shadow_offset_y, z_index
) 
SELECT 1, 0.1, 10, '#ffffff', 0.7, 
       5, 1, '#000000', 0.9,
       FALSE, '#000000', 5, 0,
       0, 10
WHERE NOT EXISTS (
    SELECT 1 FROM resolution_badge_settings WHERE user_id = 1
);

-- Create a trigger function to update the updated_at timestamp automatically
CREATE OR REPLACE FUNCTION update_resolution_badge_settings_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Drop the trigger if it exists
DROP TRIGGER IF EXISTS update_resolution_badge_settings_updated_at_trigger ON resolution_badge_settings;

-- Create the trigger
CREATE TRIGGER update_resolution_badge_settings_updated_at_trigger
BEFORE UPDATE ON resolution_badge_settings
FOR EACH ROW
EXECUTE FUNCTION update_resolution_badge_settings_updated_at();
