// Utility functions for routes

/**
 * Formats a URL to ensure it has the correct protocol and no trailing slash
 * @param {string} url The URL to format
 * @returns {string} The formatted URL
 */
export const formatUrl = (url) => {
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

/**
 * Normalize field names to handle both frontend and backend naming conventions for Jellyfin
 * @param {Object} body The request body
 * @returns {Object} Normalized object with standardized field names
 */
export const normalizeJellyfinFields = (body) => {
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

/**
 * Normalize field names to handle both frontend and backend naming conventions for AniDB
 * @param {Object} body The request body
 * @returns {Object} Normalized object with standardized field names
 */
export const normalizeAnidbFields = (body) => {
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
