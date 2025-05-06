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

// Jellyfin Libraries API Endpoints
app.get('/api/jellyfin-libraries', async (req, res) => {
  console.log('📬 API Request: GET /api/jellyfin-libraries');
  try {
    // Get the current user's Jellyfin settings
    const userId = 1; // Using default user ID
    const settings = await getJellyfinSettingsByUserId(userId);
    
    if (!settings) {
      console.log('⚠️ No Jellyfin settings found');
      return res.status(404).json({ 
        success: false, 
        message: 'No Jellyfin settings found. Please configure Jellyfin first.' 
      });
    }
    
    // Format URL
    let url = settings.jellyfin_url;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://' + url;
    }
    if (url.endsWith('/')) {
      url = url.slice(0, -1);
    }
    
    console.log(`🔍 Fetching libraries from Jellyfin at: ${url}`);
    
    // Fetch libraries from Jellyfin
    const librariesResponse = await fetch(`${url}/Users/${settings.jellyfin_user_id}/Views`, {
      headers: { 'X-Emby-Token': settings.jellyfin_api_key }
    });
    
    if (!librariesResponse.ok) {
      const errorStatus = librariesResponse.status;
      console.error(`❌ Failed to fetch Jellyfin libraries: ${errorStatus}`);
      return res.status(400).json({ 
        success: false, 
        message: `Failed to fetch libraries: Status ${errorStatus}` 
      });
    }
    
    const librariesData = await librariesResponse.json();
    console.log(`✅ Retrieved ${librariesData.Items.length} libraries`);
    
    // Get actual item counts for each library
    const librariesWithCounts = await Promise.all(librariesData.Items.map(async (library) => {
      try {
        let apiUrl = '';
        let itemCount = 0;
        
        // Different logic based on library name
        if (library.Name.toLowerCase().includes('movie')) {
          // For Movies library
          apiUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?ParentId=${library.Id}&IncludeItemTypes=Movie&Recursive=true&Limit=0&EnableTotalRecordCount=true`;
        } else if (library.Name.toLowerCase().includes('tv') || library.Name.toLowerCase().includes('television')) {
          // For TV library
          apiUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?ParentId=${library.Id}&IncludeItemTypes=Series&Recursive=true&Limit=0&EnableTotalRecordCount=true`;
        } else if (library.Name.toLowerCase().includes('anime')) {
          // For Anime library
          apiUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?ParentId=${library.Id}&IncludeItemTypes=Series&Recursive=true&Limit=0&EnableTotalRecordCount=true`;
        } else if (library.Name.toLowerCase().includes('home') || library.Name.toLowerCase().includes('video')) {
          // For Home Videos library
          apiUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?ParentId=${library.Id}&IncludeItemTypes=Video&Recursive=true&Limit=0&EnableTotalRecordCount=true`;
        } else if (library.Name.toLowerCase().includes('collection')) {
          // For Collections library
          apiUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?ParentId=${library.Id}&IncludeItemTypes=BoxSet&Recursive=true&Limit=0&EnableTotalRecordCount=true`;
        } else if (library.Name.toLowerCase().includes('playlist')) {
          // For Playlists library
          apiUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?ParentId=${library.Id}&IncludeItemTypes=Playlist&Recursive=true&Limit=0&EnableTotalRecordCount=true`;
        } else {
          // Generic approach for other libraries
          apiUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?ParentId=${library.Id}&Recursive=true&Limit=0&EnableTotalRecordCount=true`;
        }
        
        console.log(`🔍 Fetching items for ${library.Name} using URL: ${apiUrl}`);
        
        // Make the API request
        const itemsResponse = await fetch(apiUrl, {
          headers: { 'X-Emby-Token': settings.jellyfin_api_key }
        });
        
        if (itemsResponse.ok) {
          const itemsData = await itemsResponse.json();
          itemCount = itemsData.TotalRecordCount || 0;
          console.log(`✅ Library ${library.Name} has ${itemCount} items`);
        } else {
          console.error(`❌ Failed to fetch items for library ${library.Name}: ${itemsResponse.status}`);
        }
        
        return {
          id: library.Id,
          name: library.Name,
          type: library.Type,
          itemCount
        };
      } catch (err) {
        console.error(`❌ Error getting items for ${library.Name}:`, err);
        return {
          id: library.Id,
          name: library.Name,
          type: library.Type,
          itemCount: 0
        };
      }
    }));
    
    return res.json({ 
      success: true, 
      libraries: librariesWithCounts 
    });
  } catch (err) {
    console.error('❌ Error fetching Jellyfin libraries:', err);
    res.status(500).json({ success: false, message: 'Server error', error: err.message });
  }
});

// Start server
app.listen(port, () => {
  console.log(`Server running on port ${port}`);
});
