import express from 'express';
import cors from 'cors';
import pg from 'pg';
import dotenv from 'dotenv';
import fetch from 'node-fetch';
import { pool } from './db.js';
import {
  getJellyfinSettingsByUserId,
  upsertJellyfinSettings
} from './models/jellyfinSettings.js';
import {
  getOmdbSettingsByUserId,
  upsertOmdbSettings
} from './models/omdbSettings.js';
import {
  getTmdbSettingsByUserId,
  upsertTmdbSettings
} from './models/tmdbSettings.js';
import {
  getAnidbSettingsByUserId,
  upsertAnidbSettings,
  testAnidbConnection
} from './models/anidbSettings.js';


const { Pool } = pg;

// Load environment variables
dotenv.config();

const app = express();
const port = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

app.get('/api/jellyfin-settings/:userId', async (req, res) => {
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

app.get('/api/omdb-settings/:userId', async (req, res) => {
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

app.get('/api/tmdb-settings/:userId', async (req, res) => {
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

app.post('/api/jellyfin-settings/:userId', async (req, res) => {
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

app.post('/api/omdb-settings/:userId', async (req, res) => {
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

app.post('/api/tmdb-settings/:userId', async (req, res) => {
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

// AniDB API Endpoints
app.get('/api/anidb-settings/:userId', async (req, res) => {
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

app.post('/api/anidb-settings/:userId', async (req, res) => {
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

app.post('/api/test-anidb-connection', async (req, res) => {
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

app.post('/api/test-jellyfin-connection', async (req, res) => {
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

// Test an OMDb API key (without saving)
app.post('/api/test-omdb-connection', async (req, res) => {
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

// Test a TMDb API key (without saving)
app.post('/api/test-tmdb-connection', async (req, res) => {
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

// Helper functions
const formatUrl = (url) => {
  let formattedUrl = url;
  // Add http:// if no protocol is specified
  if (!formattedUrl.startsWith('http://') && !formattedUrl.startsWith('https://')) {
    formattedUrl = 'http://' + formattedUrl;
  }
  
  // Remove trailing slash if present
  if (formattedUrl.endsWith('/')) {
    formattedUrl = formattedUrl.slice(0, -1);
  }
  
  return formattedUrl;
};

// Normalize field names to handle both frontend and backend naming conventions
const normalizeJellyfinFields = (body) => {
  // Create a new object with standardized field names
  const normalized = {
    jellyfin_url: body.jellyfin_url || body.url,
    jellyfin_api_key: body.jellyfin_api_key || body.apiKey,
    jellyfin_user_id: body.jellyfin_user_id || body.userId
  };
  
  console.log('📣 [normalizeJellyfinFields] Original:', body);
  console.log('📣 [normalizeJellyfinFields] Normalized:', normalized);
  
  return normalized;
};

// Normalize AniDB field names to handle both frontend and backend naming conventions
const normalizeAnidbFields = (body) => {
  // Create a new object with standardized field names
  const normalized = {
    anidb_username: body.anidb_username || body.username,
    anidb_password: body.anidb_password || body.password,
    anidb_client: body.anidb_client || body.client,
    anidb_version: body.anidb_version || body.version,
    anidb_language: body.anidb_language || body.language || 'en',
    anidb_cache_expiration: body.anidb_cache_expiration || body.cacheExpiration || 60
  };
  
  console.log('📣 [normalizeAnidbFields] Original:', { ...body, anidb_password: '******', password: '******' });
  console.log('📣 [normalizeAnidbFields] Normalized:', { ...normalized, anidb_password: '******' });
  
  return normalized;
};


// The Jellyfin, OMDB, TMDB, and TVDB routes are already defined above
// Removing duplicate definitions

// Test connection handlers
// Removing duplicate test connection endpoints - using the ones defined earlier
/*
app.post('/api/test-jellyfin-connection', async (req, res) => {
  try {
    const { jellyfin_url, jellyfin_api_key, jellyfin_user_id } = req.body;
    
    // Validate required parameters
    if (!jellyfin_url) {
      return res.status(400).json({ message: 'Jellyfin URL is required' });
    }
    
    // Format URL properly
    const url = formatUrl(jellyfin_url);
    
    // Test connection to Jellyfin server
    try {
      // Make a request to the Jellyfin system info endpoint
      const response = await fetch(`${url}/System/Info`, {
        headers: {
          'X-MediaBrowser-Token': jellyfin_api_key || '',
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        return res.status(400).json({ 
          success: false, 
          message: `Failed to connect to Jellyfin: ${response.status} ${response.statusText}` 
        });
      }
      
      const data = await response.json();
      
      // Return success with server info
      return res.status(200).json({ 
        success: true, 
        message: 'Successfully connected to Jellyfin server',
        serverInfo: {
          serverName: data.ServerName,
          version: data.Version,
          operatingSystem: data.OperatingSystem
        }
      });
    } catch (error) {
      console.error('Error testing Jellyfin connection:', error);
      return res.status(500).json({ 
        success: false, 
        message: `Failed to connect to Jellyfin: ${error.message}` 
      });
    }
  } catch (error) {
    console.error('Error processing Jellyfin connection test:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
});

// OMDB API Routes
// Get OMDB settings for a user
app.get('/api/omdb-settings/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const result = await pool.query(
      'SELECT * FROM omdb_settings WHERE user_id = $1',
      [userId]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'OMDB settings not found for this user' });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching OMDB settings:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Create or update OMDB settings for a user
app.post('/api/omdb-settings/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { api_key } = req.body;
    
    // Check if settings already exist for this user
    const checkResult = await pool.query(
      'SELECT * FROM omdb_settings WHERE user_id = $1',
      [userId]
    );
    
    let result;
    if (checkResult.rows.length === 0) {
      // Create new settings
      result = await pool.query(
        'INSERT INTO omdb_settings (user_id, api_key) VALUES ($1, $2) RETURNING *',
        [userId, api_key]
      );
    } else {
      // Update existing settings
      result = await pool.query(
        'UPDATE omdb_settings SET api_key = $2, updated_at = CURRENT_TIMESTAMP WHERE user_id = $1 RETURNING *',
        [userId, api_key]
      );
    }
    
    res.status(200).json(result.rows[0]);
  } catch (error) {
    console.error('Error saving OMDB settings:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Test OMDB API connection
app.post('/api/test-omdb-connection', async (req, res) => {
  try {
    const { api_key } = req.body;
    
    // Validate required parameters
    if (!api_key) {
      return res.status(400).json({ message: 'OMDB API key is required' });
    }
    
    try {
      // Make a request to the OMDB API
      const response = await fetch(`http://www.omdbapi.com/?apikey=${api_key}&t=inception`);
      
      if (!response.ok) {
        return res.status(400).json({ 
          success: false, 
          message: `Failed to connect to OMDB API: ${response.status} ${response.statusText}` 
        });
      }
      
      const data = await response.json();
      
      // Check for OMDB error response
      if (data.Response === 'False') {
        return res.status(400).json({
          success: false,
          message: data.Error || 'Invalid OMDB API key'
        });
      }
      
      // Return success with API info
      return res.status(200).json({ 
        success: true, 
        message: 'Successfully connected to OMDB API',
        apiInfo: {
          title: data.Title,
          year: data.Year
        }
      });
    } catch (error) {
      console.error('Error testing OMDB connection:', error);
      return res.status(500).json({ 
        success: false, 
        message: `Failed to connect to OMDB API: ${error.message}` 
      });
    }
  } catch (error) {
    console.error('Error processing OMDB connection test:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
});

// TMDB API Routes
// Get TMDB settings for a user
app.get('/api/tmdb-settings/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const result = await pool.query(
      'SELECT * FROM tmdb_settings WHERE user_id = $1',
      [userId]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'TMDB settings not found for this user' });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching TMDB settings:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Create or update TMDB settings for a user
app.post('/api/tmdb-settings/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { api_key } = req.body;
    
    // Check if settings already exist for this user
    const checkResult = await pool.query(
      'SELECT * FROM tmdb_settings WHERE user_id = $1',
      [userId]
    );
    
    let result;
    if (checkResult.rows.length === 0) {
      // Create new settings
      result = await pool.query(
        'INSERT INTO tmdb_settings (user_id, api_key) VALUES ($1, $2) RETURNING *',
        [userId, api_key]
      );
    } else {
      // Update existing settings
      result = await pool.query(
        'UPDATE tmdb_settings SET api_key = $2, updated_at = CURRENT_TIMESTAMP WHERE user_id = $1 RETURNING *',
        [userId, api_key]
      );
    }
    
    res.status(200).json(result.rows[0]);
  } catch (error) {
    console.error('Error saving TMDB settings:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Test TMDB API connection
app.post('/api/test-tmdb-connection', async (req, res) => {
  try {
    const { api_key } = req.body;
    
    // Validate required parameters
    if (!api_key) {
      return res.status(400).json({ message: 'TMDB API key is required' });
    }
    
    try {
      // Make a request to the TMDB API
      const response = await fetch(`https://api.themoviedb.org/3/movie/550?api_key=${api_key}`);
      
      if (!response.ok) {
        return res.status(400).json({ 
          success: false, 
          message: `Failed to connect to TMDB API: ${response.status} ${response.statusText}` 
        });
      }
      
      const data = await response.json();
      
      // Return success with API info
      return res.status(200).json({ 
        success: true, 
        message: 'Successfully connected to TMDB API',
        apiInfo: {
          title: data.title,
          year: new Date(data.release_date).getFullYear()
        }
      });
    } catch (error) {
      console.error('Error testing TMDB connection:', error);
      return res.status(500).json({ 
        success: false, 
        message: `Failed to connect to TMDB API: ${error.message}` 
      });
    }
  } catch (error) {
    console.error('Error processing TMDB connection test:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
});

// TVDB API Routes
// Get TVDB settings for a user
app.get('/api/tvdb-settings/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const result = await pool.query(
      'SELECT * FROM tvdb_settings WHERE user_id = $1',
      [userId]
    );
    
    if (result.rows.length === 0) {
      return res.status(404).json({ message: 'TVDB settings not found for this user' });
    }
    
    res.json(result.rows[0]);
  } catch (error) {
    console.error('Error fetching TVDB settings:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Create or update TVDB settings for a user
app.post('/api/tvdb-settings/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const { api_key, pin } = req.body;
    
    // Check if settings already exist for this user
    const checkResult = await pool.query(
      'SELECT * FROM tvdb_settings WHERE user_id = $1',
      [userId]
    );
    
    let result;
    if (checkResult.rows.length === 0) {
      // Create new settings
      result = await pool.query(
        'INSERT INTO tvdb_settings (user_id, api_key, pin) VALUES ($1, $2, $3) RETURNING *',
        [userId, api_key, pin]
      );
    } else {
      // Update existing settings
      result = await pool.query(
        'UPDATE tvdb_settings SET api_key = $2, pin = $3, updated_at = CURRENT_TIMESTAMP WHERE user_id = $1 RETURNING *',
        [userId, api_key, pin]
      );
    }
    
    res.status(200).json(result.rows[0]);
  } catch (error) {
    console.error('Error saving TVDB settings:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// Test TVDB API connection
app.post('/api/test-tvdb-connection', async (req, res) => {
  try {
    const { api_key } = req.body;
    
    // Validate required parameters
    if (!api_key) {
      return res.status(400).json({ message: 'TVDB API key is required' });
    }
    
    try {
      // Get TVDB token first
      const loginResponse = await fetch('https://api.thetvdb.com/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ apikey: api_key })
      });
      
      if (!loginResponse.ok) {
        return res.status(400).json({ 
          success: false, 
          message: `Failed to authenticate with TVDB API: ${loginResponse.status} ${loginResponse.statusText}` 
        });
      }
      
      const loginData = await loginResponse.json();
      const token = loginData.token;
      
      // Now test the API with the token
      const response = await fetch('https://api.thetvdb.com/search/series?name=game%20of%20thrones', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        return res.status(400).json({ 
          success: false, 
          message: `Failed to connect to TVDB API: ${response.status} ${response.statusText}` 
        });
      }
      
      const data = await response.json();
      
      // Return success with API info
      return res.status(200).json({ 
        success: true, 
        message: 'Successfully connected to TVDB API',
        apiInfo: {
          series: data.data && data.data.length > 0 ? data.data[0].seriesName : 'Unknown'
        }
      });
    } catch (error) {
      console.error('Error testing TVDB connection:', error);
      return res.status(500).json({ 
        success: false, 
        message: `Failed to connect to TVDB API: ${error.message}` 
      });
    }
  } catch (error) {
    console.error('Error processing TVDB connection test:', error);
    res.status(500).json({ success: false, message: 'Server error' });
  }
});

*/

// Start server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
