import express from 'express';
import {
  getOmdbSettingsByUserId,
  upsertOmdbSettings
} from '../models/omdbSettings.js';

const router = express.Router();

/**
 * @route GET /api/omdb-settings/:userId
 * @description Retrieves OMDB settings for a specific user
 */
router.get('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  try {
    const settings = await getOmdbSettingsByUserId(userId);
    if (!settings) return res.status(404).json({ message: 'Settings not found' });
    res.json(settings);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

/**
 * @route POST /api/omdb-settings/:userId
 * @description Saves or updates OMDB settings for a specific user
 */
router.post('/:userId', async (req, res) => {
  const userId = Number(req.params.userId);
  const { api_key } = req.body;
  if (!api_key) return res.status(400).json({ message: 'Missing API key' });
  try {
    const saved = await upsertOmdbSettings({ user_id: userId, api_key });
    res.json(saved);
  } catch (err) {
    console.error(err);
    res.status(500).json({ message: 'Server error' });
  }
});

export default router;
