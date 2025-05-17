// Temporary patch file with the fix for the AniDB settings loading

// This is the fixed loadSettings function that should be added to ApiSettings.vue
const loadSettings = async () => {
  loading.value = true;
  error.value = null;
  
  try {
    const res = await api.getConfig('settings.yaml');
    const config = res.data.config;
    
    if (config && config.api_keys) {
      // Load Jellyfin settings
      if (config.api_keys.Jellyfin && config.api_keys.Jellyfin.length > 0) {
        const jellyfinConfig = config.api_keys.Jellyfin[0];
        jellyfin.url = jellyfinConfig.url || '';
        jellyfin.api_key = jellyfinConfig.api_key || '';
        jellyfin.user_id = jellyfinConfig.user_id || '';
      }
      
      // Load OMDB settings
      if (config.api_keys.OMDB && config.api_keys.OMDB.length > 0) {
        const omdbConfig = config.api_keys.OMDB[0];
        omdb.api_key = omdbConfig.api_key || '';
        omdb.cache_expiration = omdbConfig.cache_expiration || 60;
      }
      
      // Load TMDB settings
      if (config.api_keys.TMDB && config.api_keys.TMDB.length > 0) {
        const tmdbConfig = config.api_keys.TMDB[0];
        tmdb.api_key = tmdbConfig.api_key || '';
        tmdb.cache_expiration = tmdbConfig.cache_expiration || 60;
        tmdb.language = tmdbConfig.language || 'en';
        tmdb.region = tmdbConfig.region || '';
      }
      
      // Load AniDB settings - THE KEY FIX IS HERE
      if (config.api_keys.aniDB) {
        const anidbConfig = config.api_keys.aniDB;
        
        // Handle both array and object formats to ensure compatibility
        if (Array.isArray(anidbConfig)) {
          // Array format - extract from both items
          if (anidbConfig.length > 0 && anidbConfig[0]) {
            anidb.username = anidbConfig[0].username || '';
          }
          
          if (anidbConfig.length > 1 && anidbConfig[1]) {
            const secondItem = anidbConfig[1];
            anidb.password = secondItem.password || '';
            anidb.version = secondItem.version || 1;
            anidb.client_name = secondItem.client_name || '';
            anidb.language = secondItem.language || 'en';
            anidb.cache_expiration = secondItem.cache_expiration || 60;
          }
        } else if (typeof anidbConfig === 'object') {
          // Object format - backend already combined the values
          anidb.username = anidbConfig.username || '';
          anidb.password = anidbConfig.password || '';
          anidb.version = anidbConfig.version || 1;
          anidb.client_name = anidbConfig.client_name || '';
          anidb.language = anidbConfig.language || 'en';
          anidb.cache_expiration = anidbConfig.cache_expiration || 60;
        }
      }
    }
  } catch (err) {
    error.value = err.response?.data?.error || err.message || 'Failed to load API settings';
  } finally {
    loading.value = false;
  }
};

/*
INSTRUCTIONS FOR THE FIX:

1. Open the file: E:\programming\aphrodite-python\aphrodite-web\frontend\src\components\settings\ApiSettings.vue
2. Locate the loadSettings function
3. Replace the loadSettings function with the one above
4. The key issue was that the code was checking for 'length' on the aniDB config object even when it might be a plain object
5. This fix handles both formats (array and object) to ensure compatibility with the backend
*/