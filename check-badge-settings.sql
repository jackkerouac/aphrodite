-- Check badge settings schema and data

-- Check resolution badge settings
SELECT 
    'resolution_badge_settings' as table_name,
    COUNT(*) as row_count,
    STRING_AGG(DISTINCT enabled::text, ', ') as enabled_values,
    STRING_AGG(DISTINCT position, ', ') as positions_used,
    MIN(size) as min_size,
    MAX(size) as max_size
FROM resolution_badge_settings;

-- Check audio badge settings
SELECT 
    'audio_badge_settings' as table_name,
    COUNT(*) as row_count,
    STRING_AGG(DISTINCT enabled::text, ', ') as enabled_values,
    STRING_AGG(DISTINCT position, ', ') as positions_used,
    MIN(size) as min_size,
    MAX(size) as max_size
FROM audio_badge_settings;

-- Check review badge settings
SELECT 
    'review_badge_settings' as table_name,
    COUNT(*) as row_count,
    STRING_AGG(DISTINCT enabled::text, ', ') as enabled_values,
    STRING_AGG(DISTINCT position, ', ') as positions_used,
    MIN(size) as min_size,
    MAX(size) as max_size,
    STRING_AGG(DISTINCT badge_layout, ', ') as badge_layouts
FROM review_badge_settings;

-- Check for any NULL sizes which might cause issues
SELECT 'NULL sizes in resolution_badge_settings' as check_type, COUNT(*) as count
FROM resolution_badge_settings WHERE size IS NULL
UNION ALL
SELECT 'NULL sizes in audio_badge_settings' as check_type, COUNT(*) as count
FROM audio_badge_settings WHERE size IS NULL
UNION ALL
SELECT 'NULL sizes in review_badge_settings' as check_type, COUNT(*) as count
FROM review_badge_settings WHERE size IS NULL;

-- Check for enabled badges with their settings
SELECT 
    'Enabled Badges Summary' as report_type,
    SUM(CASE WHEN r.enabled = true THEN 1 ELSE 0 END) as enabled_resolution_badges,
    SUM(CASE WHEN a.enabled = true THEN 1 ELSE 0 END) as enabled_audio_badges,
    SUM(CASE WHEN rev.enabled = true THEN 1 ELSE 0 END) as enabled_review_badges
FROM resolution_badge_settings r
CROSS JOIN audio_badge_settings a
CROSS JOIN review_badge_settings rev
WHERE r.user_id = a.user_id AND a.user_id = rev.user_id;

-- Check specific settings for a user (replace 1 with actual user_id)
-- Uncomment and modify as needed
-- SELECT 
--     'Resolution' as badge_type,
--     enabled,
--     position,
--     size,
--     background_color,
--     background_opacity as transparency,
--     margin
-- FROM resolution_badge_settings
-- WHERE user_id = 1
-- UNION ALL
-- SELECT 
--     'Audio' as badge_type,
--     enabled,
--     position,
--     size,
--     background_color,
--     background_opacity as transparency,
--     margin
-- FROM audio_badge_settings
-- WHERE user_id = 1
-- UNION ALL
-- SELECT 
--     'Review' as badge_type,
--     enabled,
--     position,
--     size,
--     background_color,
--     background_opacity as transparency,
--     margin
-- FROM review_badge_settings
-- WHERE user_id = 1;
