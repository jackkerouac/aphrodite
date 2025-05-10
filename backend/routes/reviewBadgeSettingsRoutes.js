import express from 'express';
import { pool } from '../db.js';
import {
  getReviewBadgeSettingsByUserId,
  upsertReviewBadgeSettings
} from '../models/reviewBadgeSettings.js';

const router = express.Router();

/**
 * @route GET /api/review-badge-settings/:userId
 * @description Retrieves review badge settings for a specific user
 */
router.get('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  console.log(`🔍 API Request: GET /api/review-badge-settings/${userId}`);
  try {
    const settings = await getReviewBadgeSettingsByUserId(userId);
    console.log('📦 Review Badge settings from DB:', settings);
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
 * @route POST /api/review-badge-settings/:userId
 * @description Saves or updates review badge settings for a specific user
 */
router.post('/:userId', async (req, res) => {
  console.log(`📬 API Request: POST /api/review-badge-settings/${req.params.userId}`, req.body);
  const userId = Number(req.params.userId);
  
  // Extract fields from request body
  const { 
    size, 
    margin,
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
    position,
    badge_layout,
    display_sources,
    source_order,
    show_logo,
    logo_size,
    logo_position,
    logo_text_spacing,
    score_format,
    spacing,
    font_family,
    font_size,
    font_weight,
    text_color,
    text_opacity,
    enabled
  } = req.body;
  
  // Validate required fields
  const missingFields = [];
  
  if (size === undefined) missingFields.push('size');
  if (margin === undefined) missingFields.push('margin');
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
    const saved = await upsertReviewBadgeSettings({
      user_id: userId,
      size,
      margin,
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
      position,
      badge_layout,
      display_sources,
      source_order,
      show_logo,
      logo_size,
      logo_position,
      logo_text_spacing,
      score_format,
      spacing,
      font_family,
      font_size,
      font_weight,
      text_color,
      text_opacity,
      enabled
    });
    console.log('✅ Review Badge settings saved successfully:', saved);
    res.json(saved);
  } catch (err) {
    console.error('❌ Error saving Review Badge settings:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route POST /api/review-badge-settings/:userId/enabled
 * @description Updates only the enabled status for review badge settings
 */
router.post('/:userId/enabled', async (req, res) => {
  console.log(`📬 API Request: POST /api/review-badge-settings/${req.params.userId}/enabled`, req.body);
  const userId = Number(req.params.userId);
  const { enabled } = req.body;
  
  if (enabled === undefined) {
    return res.status(400).json({ message: 'Missing enabled status in request body' });
  }
  
  try {
    // Check if settings exist for this user
    const existingSettings = await getReviewBadgeSettingsByUserId(userId);
    
    if (existingSettings) {
      // Update only the enabled flag if settings exist
      const result = await pool.query(
        `UPDATE review_badge_settings SET 
          enabled = $1,
          updated_at = CURRENT_TIMESTAMP
        WHERE user_id = $2
        RETURNING *`,
        [enabled, userId]
      );
      
      console.log(`✅ Review Badge enabled status updated to ${enabled}`);
      return res.json(result.rows[0]);
    } else {
      // Create default settings with the enabled flag if none exist
      const result = await pool.query(
        `INSERT INTO review_badge_settings (
          user_id, 
          enabled,
          size,
          margin,
          position,
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
          badge_layout,
          font_family,
          font_size,
          font_weight,
          text_color,
          text_opacity,
          created_at,
          updated_at
        ) VALUES ($1, $2, 66, 10, 'bottom-left', '#000000', 0.6, 10, 1, '#000000', 0.5, false, '#000000', 5, 2, 2, 3, 'vertical', 'Arial', 24, 400, '#ffffff', 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        RETURNING *`,
        [userId, enabled]
      );
      
      console.log(`✅ Created new Review Badge settings with enabled=${enabled}`);
      return res.json(result.rows[0]);
    }
  } catch (err) {
    console.error('❌ Error updating Review Badge enabled status:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;