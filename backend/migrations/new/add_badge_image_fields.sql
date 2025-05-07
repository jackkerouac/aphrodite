-- Migration: Add badge image fields to badge settings tables

-- Add badge_image field to resolution_badge_settings if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'resolution_badge_settings' AND column_name = 'badge_image'
    ) THEN
        ALTER TABLE resolution_badge_settings
        ADD COLUMN badge_image BYTEA,
        ADD COLUMN last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
    END IF;
END$$;

-- Check if audio_badge_settings table exists, if not create it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'audio_badge_settings'
    ) THEN
        CREATE TABLE audio_badge_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            size REAL DEFAULT 0.1,
            margin REAL DEFAULT 10,
            position VARCHAR DEFAULT 'top-right',
            audio_codec_type VARCHAR DEFAULT 'auto',
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
            badge_image BYTEA,
            last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT audio_badge_settings_user_id_unique UNIQUE (user_id),
            CONSTRAINT audio_badge_settings_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Create index for faster lookups
        CREATE INDEX audio_badge_settings_user_id_idx ON audio_badge_settings(user_id);
        
        -- Create trigger for updating timestamp
        CREATE TRIGGER update_audio_badge_settings_updated_at_trigger
        BEFORE UPDATE ON audio_badge_settings
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
        
        -- Insert default settings for user ID 1
        INSERT INTO audio_badge_settings (
            user_id, size, margin, position, audio_codec_type, background_color, background_transparency, 
            border_radius, border_width, border_color, border_transparency,
            shadow_toggle, shadow_color, shadow_blur_radius, shadow_offset_x,
            shadow_offset_y, z_index
        ) 
        SELECT 1, 0.1, 10, 'top-right', 'auto', '#ffffff', 0.7, 
               5, 1, '#000000', 0.9,
               FALSE, '#000000', 5, 0,
               0, 10
        WHERE NOT EXISTS (
            SELECT 1 FROM audio_badge_settings WHERE user_id = 1
        );
    ELSE
        -- If table exists but doesn't have badge_image field, add it
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'audio_badge_settings' AND column_name = 'badge_image'
        ) THEN
            ALTER TABLE audio_badge_settings
            ADD COLUMN badge_image BYTEA,
            ADD COLUMN last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        END IF;
    END IF;
END$$;

-- Check if review_badge_settings table exists, if not create it
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.tables 
        WHERE table_name = 'review_badge_settings'
    ) THEN
        CREATE TABLE review_badge_settings (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL,
            size REAL DEFAULT 0.1,
            margin REAL DEFAULT 10,
            position VARCHAR DEFAULT 'top-left',
            review_score_type VARCHAR DEFAULT 'percentage',
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
            badge_image BYTEA,
            last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT review_badge_settings_user_id_unique UNIQUE (user_id),
            CONSTRAINT review_badge_settings_user_id_fk FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        
        -- Create index for faster lookups
        CREATE INDEX review_badge_settings_user_id_idx ON review_badge_settings(user_id);
        
        -- Create trigger for updating timestamp
        CREATE TRIGGER update_review_badge_settings_updated_at_trigger
        BEFORE UPDATE ON review_badge_settings
        FOR EACH ROW
        EXECUTE FUNCTION update_modified_column();
        
        -- Insert default settings for user ID 1
        INSERT INTO review_badge_settings (
            user_id, size, margin, position, review_score_type, background_color, background_transparency, 
            border_radius, border_width, border_color, border_transparency,
            shadow_toggle, shadow_color, shadow_blur_radius, shadow_offset_x,
            shadow_offset_y, z_index
        ) 
        SELECT 1, 0.1, 10, 'top-left', 'percentage', '#ffffff', 0.7, 
               5, 1, '#000000', 0.9,
               FALSE, '#000000', 5, 0,
               0, 10
        WHERE NOT EXISTS (
            SELECT 1 FROM review_badge_settings WHERE user_id = 1
        );
    ELSE
        -- If table exists but doesn't have badge_image field, add it
        IF NOT EXISTS (
            SELECT 1 FROM information_schema.columns 
            WHERE table_name = 'review_badge_settings' AND column_name = 'badge_image'
        ) THEN
            ALTER TABLE review_badge_settings
            ADD COLUMN badge_image BYTEA,
            ADD COLUMN last_generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP;
        END IF;
    END IF;
END$$;