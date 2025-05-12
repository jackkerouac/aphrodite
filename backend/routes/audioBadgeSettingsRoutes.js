import express from 'express';
import { pool } from '../db.js';
import {
  getAudioBadgeSettingsByUserId,
  upsertAudioBadgeSettings
} from '../models/audioBadgeSettings.js';

const router = express.Router();

/**
 * @route GET /api/audio-badge-settings/:userId
 * @description Retrieves audio badge settings for a specific user
 */
router.get('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  console.log(`🔍 API Request: GET /api/audio-badge-settings/${userId}`);
  try {
    const settings = await getAudioBadgeSettingsByUserId(userId);
    console.log('📦 Audio Badge settings from DB:', settings);
    if (!settings) {
      console.log('⚠️ No settings found for this user');
      return res.status(404).json({ message: 'Settings not found' });
    }
    console.log('✅ Returning settings:', settings);
    res.json(settings);
  } catch (err) {
    console.error('❌ Server error:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route POST /api/audio-badge-settings/:userId
 * @description Saves or updates audio badge settings for a specific user
 */
router.post('/:userId', async (req, res) => {
  console.log(`📬 API Request: POST /api/audio-badge-settings/${req.params.userId}`);
  console.log('📦 Request body:', JSON.stringify(req.body, null, 2)); 
  console.log('📊 Badge image received:', !!req.body.badge_image); 
  if (req.body.badge_image) { 
    console.log(`📏 Badge image length: ${req.body.badge_image.length}`); 
    console.log(`🔍 Badge image preview: ${req.body.badge_image.substring(0, 50)}...`); 
  } else { 
    console.log('⚠️ No badge image in request body'); 
  }
  const userId = Number(req.params.userId);
  
  // Extract and normalize fields from request body
  const body = req.body;
  
  // Support both camelCase and snake_case field names
  const size = body.size;
  const margin = body.margin;
  const position = body.position;
  const codec_type = body.codec_type || body.codecType || body.audio_codec_type;
  const background_color = body.background_color || body.backgroundColor;
  // Support both opacity and transparency naming
  const background_opacity = body.background_opacity !== undefined ? body.background_opacity : 
                            (body.background_transparency !== undefined ? body.background_transparency : 
                            (body.backgroundOpacity !== undefined ? body.backgroundOpacity : body.backgroundTransparency));
  const border_radius = body.border_radius || body.borderRadius;
  const border_width = body.border_width || body.borderWidth;
  const border_color = body.border_color || body.borderColor;
  const border_opacity = body.border_opacity !== undefined ? body.border_opacity : 
                        (body.border_transparency !== undefined ? body.border_transparency : 
                        (body.borderOpacity !== undefined ? body.borderOpacity : body.borderTransparency));
  const shadow_enabled = body.shadow_enabled !== undefined ? body.shadow_enabled : 
                        (body.shadow_toggle !== undefined ? body.shadow_toggle : 
                        (body.shadowEnabled !== undefined ? body.shadowEnabled : body.shadowToggle));
  const shadow_color = body.shadow_color || body.shadowColor;
  const shadow_blur = body.shadow_blur || body.shadow_blur_radius || body.shadowBlur;
  const shadow_offset_x = body.shadow_offset_x || body.shadowOffsetX;
  const shadow_offset_y = body.shadow_offset_y || body.shadowOffsetY;
  const z_index = body.z_index || body.zIndex;
  const badge_image = body.badge_image;
  const enabled = body.enabled;
  const text_color = body.text_color || body.textColor;
  const font_family = body.font_family || body.fontFamily;
  const font_size = body.font_size || body.fontSize;
  const use_brand_colors = body.use_brand_colors !== undefined ? body.use_brand_colors : 
                          (body.useBrandColors !== undefined ? body.useBrandColors : true);
  
  // Validate required fields
  const missingFields = [];
  
  if (size === undefined) missingFields.push('size');
  if (margin === undefined) missingFields.push('margin');
  if (!position) missingFields.push('position');
  if (!codec_type) missingFields.push('codec_type');
  if (!background_color) missingFields.push('background_color');
  if (background_opacity === undefined) missingFields.push('background_opacity');
  if (border_radius === undefined) missingFields.push('border_radius');
  if (border_width === undefined) missingFields.push('border_width');
  if (!border_color) missingFields.push('border_color');
  if (border_opacity === undefined) missingFields.push('border_opacity');
  if (z_index === undefined) missingFields.push('z_index');
  
  if (missingFields.length > 0) {
    const errorMessage = `Missing required fields: ${missingFields.join(', ')}`;
    console.log(`⚠️ ${errorMessage}`);
    console.log('⚠️ Received body:', req.body);
    return res.status(400).json({ message: errorMessage });
  }
  
  try {
    const saved = await upsertAudioBadgeSettings({
      user_id: userId,
      size,
      margin,
      position,
      codec_type,
      background_color,
      background_opacity,
      border_radius,
      border_width,
      border_color,
      border_opacity,
      shadow_enabled,
      shadow_color,
      shadow_blur,
      shadow_offset_x,
      shadow_offset_y,
      z_index,
      badge_image,
      enabled,
      text_color,
      font_family,
      font_size,
      use_brand_colors
    });
    console.log('✅ Audio Badge settings saved successfully:', saved);
    res.json(saved);
  } catch (err) {
    console.error('❌ Error saving Audio Badge settings:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route GET /api/audio-badge-settings/:userId/enabled
 * @description Get only the enabled status for audio badge settings
 */
router.get('/:userId/enabled', async (req, res) => {
  const userId = Number(req.params.userId);
  console.log(`🔍 API Request: GET /api/audio-badge-settings/${userId}/enabled`);
  
  try {
    const result = await pool.query(
      'SELECT enabled FROM audio_badge_settings WHERE user_id = $1',
      [userId]
    );
    
    if (result.rows.length === 0) {
      console.log('⚠️ No settings found for this user, returning false');
      return res.json({ enabled: false });
    }
    
    console.log('✅ Returning enabled status:', result.rows[0].enabled);
    res.json({ enabled: result.rows[0].enabled });
  } catch (err) {
    console.error('❌ Server error:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route POST /api/audio-badge-settings/:userId/enabled
 * @description Updates only the enabled status for audio badge settings
 */
router.post('/:userId/enabled', async (req, res) => {
  console.log(`📬 API Request: POST /api/audio-badge-settings/${req.params.userId}/enabled`, req.body);
  const userId = Number(req.params.userId);
  const { enabled } = req.body;
  
  if (enabled === undefined) {
    return res.status(400).json({ message: 'Missing enabled status in request body' });
  }
  
  try {
    // Check if settings exist for this user
    const existingSettings = await getAudioBadgeSettingsByUserId(userId);
    
    if (existingSettings) {
      // Update only the enabled flag if settings exist
      const result = await pool.query(
        `UPDATE audio_badge_settings SET 
          enabled = $1,
          updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $2
        RETURNING *`,
        [enabled, userId]
      );
      
      console.log(`✅ Audio Badge enabled status updated to ${enabled}`);
      return res.json(result.rows[0]);
    } else {
      // Create default settings with the enabled flag if none exist
      const result = await pool.query(
        `INSERT INTO audio_badge_settings (
          user_id, 
          enabled,
          size,
          margin,
          position,
          codec_type,
          background_color,
          background_opacity,
          border_radius,
          border_width,
          border_color,
          border_opacity,
          shadow_enabled,
          shadow_color,
          shadow_blur,
          shadow_offset_x,
          shadow_offset_y,
          z_index,
          created_at,
          updated_at
        ) VALUES ($1, $2, 100, 10, 'top-left', 'hra', '#000000', 0.6, 10, 1, '#000000', 0.5, false, '#000000', 5, 2, 2, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING *`,
        [userId, enabled]
      );
      
      console.log(`✅ Created new Audio Badge settings with enabled=${enabled}`);
      return res.json(result.rows[0]);
    }
  } catch (err) {
    console.error('❌ Error updating Audio Badge enabled status:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;