import express from 'express';
import { normalizeJellyfinFields } from './utils.js';
import {
  getJellyfinSettingsByUserId,
  upsertJellyfinSettings
} from '../models/jellyfinSettings.js';

const router = express.Router();

/**
 * @route GET /api/jellyfin-settings/:userId
 * @description Retrieves Jellyfin settings for a specific user
 */
router.get('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  console.log(`🔍 API Request: GET /api/jellyfin-settings/${userId}`);
  try {
    const settings = await getJellyfinSettingsByUserId(userId);
    console.log('📦 Jellyfin settings from DB:', settings);
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
 * @route POST /api/jellyfin-settings/:userId
 * @description Saves or updates Jellyfin settings for a specific user
 */
router.post('/:userId', async (req, res) => {
  console.log(`📬 API Request: POST /api/jellyfin-settings/${req.params.userId}`, req.body);
  const userId = Number(req.params.userId);
  
  // Normalize fields to handle both naming conventions
  const normalizedBody = normalizeJellyfinFields(req.body);
  const { jellyfin_url, jellyfin_api_key, jellyfin_user_id } = normalizedBody;
  
  if (!jellyfin_url || !jellyfin_api_key || !jellyfin_user_id) {
    console.log('⚠️ Missing required fields in save request');
    return res.status(400).json({ message: 'Missing required fields' });
  }
  try {
    const saved = await upsertJellyfinSettings({
      user_id: userId,
      jellyfin_url,
      jellyfin_api_key,
      jellyfin_user_id
    });
    console.log('✅ Jellyfin settings saved successfully:', saved);
    res.json(saved);
  } catch (err) {
    console.error('❌ Error saving Jellyfin settings:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;
