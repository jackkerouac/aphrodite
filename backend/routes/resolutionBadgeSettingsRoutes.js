import express from 'express';
import { pool } from '../db.js';
import {
  getResolutionBadgeSettingsByUserId,
  upsertResolutionBadgeSettings
} from '../models/resolutionBadgeSettings.js';

const router = express.Router();

/**
 * @route GET /api/resolution-badge-settings/:userId
 * @description Retrieves resolution badge settings for a specific user
 */
router.get('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  console.log(`🔍 API Request: GET /api/resolution-badge-settings/${userId}`);
  try {
    const settings = await getResolutionBadgeSettingsByUserId(userId);
    console.log('📦 Resolution Badge settings from DB:', settings);
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
 * @route POST /api/resolution-badge-settings/:userId
 * @description Saves or updates resolution badge settings for a specific user
 */
router.post('/:userId', async (req, res) => {
  console.log(`📬 API Request: POST /api/resolution-badge-settings/${req.params.userId}`, req.body);
  const userId = Number(req.params.userId);
  
  // Extract and normalize fields from request body
  const body = req.body;
  
  // Support both camelCase and snake_case field names
  const size = body.size;
  const margin = body.margin;
  const position = body.position;
  const resolution_type = body.resolution_type || body.resolutionType;
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
  const enabled = body.enabled;
  const use_brand_colors = body.use_brand_colors !== undefined ? body.use_brand_colors : 
                         (body.useBrandColors !== undefined ? body.useBrandColors : true);
  
  // Validate required fields
  const missingFields = [];
  
  if (size === undefined) missingFields.push('size');
  if (margin === undefined) missingFields.push('margin');
  if (!position) missingFields.push('position');
  if (!resolution_type) missingFields.push('resolution_type');
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
    const saved = await upsertResolutionBadgeSettings({
      user_id: userId,
      size,
      margin,
      position,
      resolution_type,
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
      enabled,
      use_brand_colors
    });
    console.log('✅ Resolution Badge settings saved successfully:', saved);
    res.json(saved);
  } catch (err) {
    console.error('❌ Error saving Resolution Badge settings:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route GET /api/resolution-badge-settings/:userId/enabled
 * @description Get only the enabled status for resolution badge settings
 */
router.get('/:userId/enabled', async (req, res) => {
  const userId = Number(req.params.userId);
  console.log(`🔍 API Request: GET /api/resolution-badge-settings/${userId}/enabled`);
  
  try {
    const result = await pool.query(
      'SELECT enabled FROM resolution_badge_settings WHERE user_id = $1',
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
 * @route POST /api/resolution-badge-settings/:userId/enabled
 * @description Updates only the enabled status for resolution badge settings
 */
router.post('/:userId/enabled', async (req, res) => {
  console.log(`📬 API Request: POST /api/resolution-badge-settings/${req.params.userId}/enabled`, req.body);
  const userId = Number(req.params.userId);
  const { enabled } = req.body;
  
  if (enabled === undefined) {
    return res.status(400).json({ message: 'Missing enabled status in request body' });
  }
  
  try {
    // Check if settings exist for this user
    const existingSettings = await getResolutionBadgeSettingsByUserId(userId);
    
    if (existingSettings) {
      // Update only the enabled flag if settings exist
      const result = await pool.query(
        `UPDATE resolution_badge_settings SET 
          enabled = $1,
          updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $2
        RETURNING *`,
        [enabled, userId]
      );
      
      console.log(`✅ Resolution Badge enabled status updated to ${enabled}`);
      return res.json(result.rows[0]);
    } else {
      // Create default settings with the enabled flag if none exist
      const result = await pool.query(
        `INSERT INTO resolution_badge_settings (
          user_id, 
          enabled,
          size,
          margin,
          position,
          resolution_type,
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
        ) VALUES ($1, $2, 152, 10, 'top-right', '1080p', '#000000', 0.6, 6, 1, '#000000', 0.5, false, '#000000', 5, 2, 2, 2, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING *`,
        [userId, enabled]
      );
      
      console.log(`✅ Created new Resolution Badge settings with enabled=${enabled}`);
      return res.json(result.rows[0]);
    }
  } catch (err) {
    console.error('❌ Error updating Resolution Badge enabled status:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;