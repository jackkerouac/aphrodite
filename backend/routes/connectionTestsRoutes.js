import express from 'express';
import fetch from 'node-fetch';
import { normalizeJellyfinFields, normalizeAnidbFields } from './utils.js';
import { testAnidbConnection } from '../models/anidbSettings.js';

const router = express.Router();

/**
 * @route POST /api/test-jellyfin-connection
 * @description Tests the connection to Jellyfin using provided credentials
 */
router.post('/test-jellyfin-connection', async (req, res) => {
  console.log('📬 API Request: POST /api/test-jellyfin-connection', req.body);
  
  // Normalize fields to handle both naming conventions
  const normalizedBody = normalizeJellyfinFields(req.body);
  const { jellyfin_url, jellyfin_api_key, jellyfin_user_id } = normalizedBody;
  
  if (!jellyfin_url || !jellyfin_api_key || !jellyfin_user_id) {
    console.log('⚠️ Missing required fields in test connection request');
    return res.status(400).json({ success: false, message: 'Missing required fields' });
  }

  try {
    // Format URL
    let url = jellyfin_url;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://' + url;
    }
    if (url.endsWith('/')) {
      url = url.slice(0, -1);
    }
    
    const endpoint = `${url}/Users/${jellyfin_user_id}`;
    console.log(`🔍 Testing connection to Jellyfin at: ${endpoint}`);

    // Test the connection
    const response = await fetch(endpoint, {
      headers: { 'X-Emby-Token': jellyfin_api_key }
    });

    if (!response.ok) {
      const errorStatus = response.status;
      let errorMessage = `Received status ${errorStatus}`;
      
      try {
        // Try to get more details from response if possible
        const errorData = await response.json();
        if (errorData && errorData.message) {
          errorMessage = errorData.message;
        }
      } catch (parseError) {
        // Ignore parse errors - use default message
      }
      
      console.error(`❌ Jellyfin connection test failed with status ${errorStatus}: ${errorMessage}`);
      return res.status(400).json({ success: false, error: errorMessage });
    }

    console.log('✅ Jellyfin connection test successful');
    return res.json({ success: true });
  } catch (err) {
    console.error('❌ Jellyfin test failed:', err.message);
    return res.status(400).json({ success: false, error: err.message });
  }
});

/**
 * @route POST /api/test-omdb-connection
 * @description Tests the connection to OMDB using provided API key
 */
router.post('/test-omdb-connection', async (req, res) => {
  const { api_key } = req.body;
  if (!api_key) return res.status(400).json({ success: false, message: 'Missing API key' });

  try {
    // Hit the example title endpoint (you can choose any valid parameter)
    const response = await fetch(`http://www.omdbapi.com/?apikey=${api_key}&t=Inception`);
    const data = await response.json();

    if (data.Response === 'False') {
      throw new Error(data.Error || 'Unknown OMDb error');
    }
    return res.json({ success: true });
  } catch (err) {
    console.error('OMDb test failed:', err);
    return res.status(400).json({ success: false, error: err.toString() });
  }
});

/**
 * @route POST /api/test-tmdb-connection
 * @description Tests the connection to TMDB using provided API key
 */
router.post('/test-tmdb-connection', async (req, res) => {
  const { api_key } = req.body;
  if (!api_key) return res.status(400).json({ success: false, message: 'Missing API key' });

  try {
    // Hit a known TMDb endpoint (e.g. movie 550 = Fight Club)
    const response = await fetch(`https://api.themoviedb.org/3/movie/550?api_key=${api_key}`);
    if (!response.ok) {
      throw new Error(`Status ${response.status}`);
    }
    const data = await response.json();
    if (!data.id) {
      throw new Error('Unexpected response');
    }
    return res.json({ success: true });
  } catch (err) {
    console.error('TMDb test failed:', err);
    return res.status(400).json({ success: false, error: err.toString() });
  }
});

/**
 * @route POST /api/test-anidb-connection
 * @description Tests the connection to AniDB using provided credentials
 */
router.post('/test-anidb-connection', async (req, res) => {
  console.log('📬 API Request: POST /api/test-anidb-connection', { ...req.body, anidb_password: '******' });
  
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
    console.log('⚠️ Missing required fields in test connection request');
    return res.status(400).json({ success: false, message: 'Missing required fields' });
  }

  try {
    await testAnidbConnection({
      anidb_username,
      anidb_password,
      anidb_client,
      anidb_version,
      anidb_language,
      anidb_cache_expiration
    });
    
    console.log('✅ AniDB connection test successful');
    return res.json({ success: true, message: 'Successfully connected to AniDB' });
  } catch (err) {
    console.error('❌ AniDB test failed:', err.message);
    return res.status(400).json({ success: false, error: err.message });
  }
});

export default router;
