import express from 'express';
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
  
  // Extract fields from request body
  const { 
    size, 
    margin, 
    position,
    audio_codec_type,
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
    badge_image
  } = req.body;
  
  // Validate required fields
  const missingFields = [];
  
  if (size === undefined) missingFields.push('size');
  if (margin === undefined) missingFields.push('margin');
  if (!position) missingFields.push('position');
  if (!audio_codec_type) missingFields.push('audio_codec_type');
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
    const saved = await upsertAudioBadgeSettings({
      user_id: userId,
      size,
      margin,
      position,
      audio_codec_type,
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
      badge_image
    });
    console.log('✅ Audio Badge settings saved successfully:', saved);
    res.json(saved);
  } catch (err) {
    console.error('❌ Error saving Audio Badge settings:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;