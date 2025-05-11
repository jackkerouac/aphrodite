-- Add use_brand_colors column to all badge settings tables

-- Add to review_badge_settings table
ALTER TABLE review_badge_settings 
ADD COLUMN IF NOT EXISTS use_brand_colors BOOLEAN DEFAULT TRUE;

-- Add to audio_badge_settings table
ALTER TABLE audio_badge_settings 
ADD COLUMN IF NOT EXISTS use_brand_colors BOOLEAN DEFAULT TRUE;

-- Add to resolution_badge_settings table
ALTER TABLE resolution_badge_settings 
ADD COLUMN IF NOT EXISTS use_brand_colors BOOLEAN DEFAULT TRUE;

-- Set default value for existing records (making brand colors on by default)
UPDATE review_badge_settings SET use_brand_colors = TRUE WHERE use_brand_colors IS NULL;
UPDATE audio_badge_settings SET use_brand_colors = TRUE WHERE use_brand_colors IS NULL;
UPDATE resolution_badge_settings SET use_brand_colors = TRUE WHERE use_brand_colors IS NULL;
