import express from 'express';
import fetch from 'node-fetch';
import { getJellyfinSettingsByUserId } from '../models/jellyfinSettings.js';

const router = express.Router();

/**
 * @route GET /api/jellyfin-libraries
 * @description Retrieves all libraries from the configured Jellyfin server
 */
router.get('/', async (req, res) => {
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

export default router;
