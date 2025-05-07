import express from 'express';
import { normalizeAnidbFields } from './utils.js';
import {
  getAnidbSettingsByUserId,
  upsertAnidbSettings
} from '../models/anidbSettings.js';

const router = express.Router();

/**
 * @route GET /api/anidb-settings/:userId
 * @description Retrieves AniDB settings for a specific user
 */
router.get('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  console.log(`🔍 API Request: GET /api/anidb-settings/${userId}`);
  try {
    const settings = await getAnidbSettingsByUserId(userId);
    console.log('📦 AniDB settings from DB:', settings);
    if (!settings) {
      console.log('⚠️ No AniDB settings found for this user');
      return res.status(404).json({ message: 'Settings not found' });
    }
    console.log('✅ Returning AniDB settings');
    res.json(settings);
  } catch (err) {
    console.error('❌ Server error:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route POST /api/anidb-settings/:userId
 * @description Saves or updates AniDB settings for a specific user
 */
router.post('/:userId', async (req, res) => {
  console.log(`📬 API Request: POST /api/anidb-settings/${req.params.userId}`, req.body);
  const userId = Number(req.params.userId);
  
  // Normalize fields to handle both naming conventions
  const normalizedBody = normalizeAnidbFields(req.body);
  const { 
    anidb_username, 
    anidb_password, 
    anidb_client, 
    anidb_version, 
    anidb_language, 
    anidb_cache_expiration 
  } = normalizedBody;
  
  // Validate required fields
  if (!anidb_username || !anidb_password || !anidb_client || !anidb_version) {
    console.log('⚠️ Missing required fields in save request');
    return res.status(400).json({ message: 'Missing required fields' });
  }

  try {
    const saved = await upsertAnidbSettings({
      user_id: userId,
      anidb_username,
      anidb_password,
      anidb_client,
      anidb_version,
      anidb_language,
      anidb_cache_expiration
    });
    console.log('✅ AniDB settings saved successfully:', { ...saved, anidb_password: '******' });
    res.json(saved);
  } catch (err) {
    console.error('❌ Error saving AniDB settings:', err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;
