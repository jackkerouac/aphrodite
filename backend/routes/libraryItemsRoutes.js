import express from 'express';
import fetch from 'node-fetch';
import { getJellyfinSettingsByUserId } from '../models/jellyfinSettings.js';

const router = express.Router();

/**
 * @route GET /api/library-items
 * @description Retrieves items from specified libraries with pagination
 */
router.get('/:userId?', async (req, res) => {
  console.log('📬 API Request: GET /api/library-items');
  console.log('Request params:', req.params);
  console.log('Request query:', req.query);
  
  try {
    const { 
      libraryIds, 
      page = 1, 
      limit = 50, 
      search = '',
      all = false 
    } = req.query;
    
    if (!libraryIds) {
      return res.status(400).json({
        success: false,
        message: 'libraryIds parameter is required'
      });
    }
    
    // Parse library IDs
    const libraryIdArray = libraryIds.split(',').filter(id => id);
    if (libraryIdArray.length === 0) {
      return res.status(400).json({
        success: false,
        message: 'No valid library IDs provided'
      });
    }
    
    // Get the current user's Jellyfin settings
    const userId = parseInt(req.params.userId || '1'); // Convert to integer
    console.log('👤 User ID for query:', userId);
    const settings = await getJellyfinSettingsByUserId(userId);
    
    if (!settings) {
      console.log('⚠️ No Jellyfin settings found for user ID:', userId);
      return res.status(404).json({ 
        success: false, 
        message: 'No Jellyfin settings found. Please configure Jellyfin first.' 
      });
    }
    console.log(`🔍 Found Jellyfin settings for user ${userId}:`, settings.jellyfin_url);
    
    // Format URL
    let url = settings.jellyfin_url;
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://' + url;
    }
    if (url.endsWith('/')) {
      url = url.slice(0, -1);
    }
    
    console.log(`🔍 Fetching items from libraries: ${libraryIdArray.join(', ')} for user ${userId}`);
    
    // Fetch items from each library
    const allItems = [];
    for (const libraryId of libraryIdArray) {
      try {
        // Build query parameters for Jellyfin API
        const params = new URLSearchParams({
          ParentId: libraryId,
          Recursive: 'true',
          Fields: 'PrimaryImageAspectRatio,BasicSyncInfo,ProductionYear,MediaSources',
          IncludeItemTypes: 'Movie,Series',
          ImageTypeLimit: '1',
          EnableImageTypes: 'Primary,Backdrop,Banner,Thumb'
        });
        
        // Add search if provided
        if (search) {
          params.append('SearchTerm', search);
        }
        
        // If fetching all items, set a high limit
        if (all === 'true') {
          params.append('Limit', '10000');
        } else {
          params.append('Limit', limit.toString());
          params.append('StartIndex', ((parseInt(page) - 1) * parseInt(limit)).toString());
        }
        
        const itemsUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?${params}`;
        const response = await fetch(itemsUrl, {
          headers: { 'X-Emby-Token': settings.jellyfin_api_key }
        });
        
        if (!response.ok) {
          console.error(`❌ Failed to fetch items from library ${libraryId}: ${response.status}`);
          continue;
        }
        
        const data = await response.json();
        
        // Transform items to match our frontend interface
        const items = data.Items.map(item => ({
          id: item.Id,
          title: item.Name,
          year: item.ProductionYear?.toString(),
          type: item.Type === 'Movie' ? 'Movie' : 'Series',
          posterUrl: item.ImageTags?.Primary ? 
            `${url}/Items/${item.Id}/Images/Primary?tag=${item.ImageTags.Primary}` : null,
          overview: item.Overview,
          mediaType: item.MediaType,
          path: item.Path,
          serverId: item.ServerId
        }));
        
        allItems.push(...items);
      } catch (err) {
        console.error(`❌ Error fetching items from library ${libraryId}:`, err);
      }
    }
    
    // If fetching all items, return them directly
    if (all === 'true') {
      return res.json({
        success: true,
        items: allItems
      });
    }
    
    // Since we've fetched from multiple libraries with their own pagination,
    // we need to get a total count separately
    let totalCount = 0;
    
    // Fetch total counts for each library
    for (const libraryId of libraryIdArray) {
      try {
        const countParams = new URLSearchParams({
          ParentId: libraryId,
          Recursive: 'true',
          IncludeItemTypes: 'Movie,Series',
          Limit: '0',
          EnableTotalRecordCount: 'true'
        });
        
        if (search) {
          countParams.append('SearchTerm', search);
        }
        
        const countUrl = `${url}/Users/${settings.jellyfin_user_id}/Items?${countParams}`;
        const countResponse = await fetch(countUrl, {
          headers: { 'X-Emby-Token': settings.jellyfin_api_key }
        });
        
        if (countResponse.ok) {
          const countData = await countResponse.json();
          totalCount += countData.TotalRecordCount || 0;
        }
      } catch (err) {
        console.error(`❌ Error getting count for library ${libraryId}:`, err);
      }
    }
    
    // Calculate pagination info
    const pageNum = parseInt(page);
    const limitNum = parseInt(limit);
    const hasMore = pageNum * limitNum < totalCount;
    
    const response = {
      success: true,
      items: allItems,
      total: totalCount,
      page: pageNum,
      limit: limitNum,
      hasMore
    };
    
    console.log(`📦 Sending response: ${response.items.length} items, total: ${response.total}, page: ${response.page}`);
    return res.json(response);
    
  } catch (err) {
    console.error('❌ Error fetching library items:', err);
    res.status(500).json({ success: false, message: 'Server error', error: err.message });
  }
});

export default router;
