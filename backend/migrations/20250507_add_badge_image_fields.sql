-- Migration: Add badge image fields (May 7, 2025)

-- First, check if the audio_badge_settings table exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'audio_badge_settings'
    ) THEN
        -- Create audio_badge_settings table with badge_image field
        CREATE TABLE audio_badge_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            size REAL DEFAULT 100,
            margin REAL DEFAULT 10,
            position VARCHAR(20) DEFAULT 'top-right',
            audio_codec_type VARCHAR(20) DEFAULT 'dolby_atmos',
            background_color VARCHAR(20) DEFAULT '#000000',
            background_transparency REAL DEFAULT 0.8,
            border_radius REAL DEFAULT 4,
            border_width REAL DEFAULT 1,
            border_color VARCHAR(20) DEFAULT '#ffffff',
            border_transparency REAL DEFAULT 0.8,
            shadow_toggle BOOLEAN DEFAULT FALSE,
            shadow_color VARCHAR(20) DEFAULT '#000000',
            shadow_blur_radius REAL DEFAULT 5,
            shadow_offset_x REAL DEFAULT 0,
            shadow_offset_y REAL DEFAULT 0,
            z_index INTEGER DEFAULT 1,
            badge_image BYTEA,
            last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT audio_badge_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Create trigger for updated_at
        CREATE TRIGGER update_audio_badge_settings_modtime
        BEFORE UPDATE ON audio_badge_settings
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
    ELSE
        -- Table exists, check if badge_image column exists
        IF NOT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'audio_badge_settings'
            AND column_name = 'badge_image'
        ) THEN
            -- Add badge_image column
            ALTER TABLE audio_badge_settings
            ADD COLUMN badge_image BYTEA,
            ADD COLUMN last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        END IF;
    END IF;
END
$$;

-- Check if the resolution_badge_settings table exists
DO $$
BEGIN
    IF EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'resolution_badge_settings'
    ) THEN
        -- Check if badge_image column exists
        IF NOT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'resolution_badge_settings'
            AND column_name = 'badge_image'
        ) THEN
            -- Add badge_image column
            ALTER TABLE resolution_badge_settings
            ADD COLUMN badge_image BYTEA,
            ADD COLUMN last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        END IF;
    END IF;
END
$$;

-- Check if the review_badge_settings table exists
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = 'review_badge_settings'
    ) THEN
        -- Create review_badge_settings table with badge_image field
        CREATE TABLE review_badge_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            size REAL DEFAULT 100,
            margin REAL DEFAULT 10,
            position VARCHAR(20) DEFAULT 'top-left',
            review_type VARCHAR(20) DEFAULT 'percentage',
            background_color VARCHAR(20) DEFAULT '#000000',
            background_transparency REAL DEFAULT 0.8,
            border_radius REAL DEFAULT 4,
            border_width REAL DEFAULT 1,
            border_color VARCHAR(20) DEFAULT '#ffffff',
            border_transparency REAL DEFAULT 0.8,
            shadow_toggle BOOLEAN DEFAULT FALSE,
            shadow_color VARCHAR(20) DEFAULT '#000000',
            shadow_blur_radius REAL DEFAULT 5,
            shadow_offset_x REAL DEFAULT 0,
            shadow_offset_y REAL DEFAULT 0,
            z_index INTEGER DEFAULT 1,
            badge_image BYTEA,
            last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT review_badge_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Create trigger for updated_at
        CREATE TRIGGER update_review_badge_settings_modtime
        BEFORE UPDATE ON review_badge_settings
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
    ELSE
        -- Table exists, check if badge_image column exists
        IF NOT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = 'review_badge_settings'
            AND column_name = 'badge_image'
        ) THEN
            -- Add badge_image column
            ALTER TABLE review_badge_settings
            ADD COLUMN badge_image BYTEA,
            ADD COLUMN last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        END IF;
    END IF;
END
$$;

-- Create default settings for user ID 1 if not already present
INSERT INTO audio_badge_settings (
    user_id, size, margin, position, audio_codec_type,
    background_color, background_transparency, 
    border_radius, border_width, border_color, border_transparency,
    shadow_toggle, shadow_color, shadow_blur_radius, shadow_offset_x, shadow_offset_y,
    z_index
) 
SELECT 
    1, 100, 10, 'top-right', 'dolby_atmos',
    '#000000', 0.8, 
    4, 1, '#ffffff', 0.8,
    FALSE, '#000000', 5, 0, 0,
    1
WHERE NOT EXISTS (
    SELECT 1 FROM audio_badge_settings WHERE user_id = 1
);
