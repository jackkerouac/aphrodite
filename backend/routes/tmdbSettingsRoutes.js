import express from 'express';
import {
  getTmdbSettingsByUserId,
  upsertTmdbSettings
} from '../models/tmdbSettings.js';

const router = express.Router();

/**
 * @route GET /api/tmdb-settings/:userId
 * @description Retrieves TMDB settings for a specific user
 */
router.get('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  try {
    const settings = await getTmdbSettingsByUserId(userId);
    if (!settings) return res.status(404).json({ message: 'Settings not found' });
    res.json(settings);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route POST /api/tmdb-settings/:userId
 * @description Saves or updates TMDB settings for a specific user
 */
router.post('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  const { api_key } = req.body;
  if (!api_key) return res.status(400).json({ message: 'Missing API key' });
  try {
    const saved = await upsertTmdbSettings({ user_id: userId, api_key });
    res.json(saved);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;
