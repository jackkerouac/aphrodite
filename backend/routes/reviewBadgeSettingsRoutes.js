import express from 'express';
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
    background_transparency,
    border_radius,
    border_width,
    border_color,
    border_transparency,
    shadow_toggle,
    shadow_color,
    shadow_blur_radius,
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
    text_transparency
  } = req.body;
  
  // Validate required fields
  const missingFields = [];
  
  if (size === undefined) missingFields.push('size');
  if (margin === undefined) missingFields.push('margin');
  if (!background_color) missingFields.push('background_color');
  if (background_transparency === undefined) missingFields.push('background_transparency');
  if (border_radius === undefined) missingFields.push('border_radius');
  if (border_width === undefined) missingFields.push('border_width');
  if (!border_color) missingFields.push('border_color');
  if (border_transparency === undefined) missingFields.push('border_transparency');
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
      background_transparency,
      border_radius,
      border_width,
      border_color,
      border_transparency,
      shadow_toggle,
      shadow_color,
      shadow_blur_radius,
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
      text_transparency
    });
    console.log('✅ Review Badge settings saved successfully:', saved);
    res.json(saved);
  } catch (err) {
    console.error('❌ Error saving Review Badge settings:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;