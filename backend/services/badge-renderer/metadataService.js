import fetch from 'node-fetch';
import { pool as db } from '../../db.js';

class MetadataService {
  constructor() {
    this.cache = new Map();
    this.cacheExpiry = 3600000; // 1 hour
  }

  async fetchItemMetadata(item, userId) {
    console.log('fetchItemMetadata called with item:', item);
    const cacheKey = `${item.jellyfin_id}-${item.media_type}`;
    
    // Check cache first
    if (this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < this.cacheExpiry) {
        return cached.data;
      }
    }

    // Fetch from Jellyfin first to get basic media info
    const jellyfinData = await this.fetchJellyfinData(item.jellyfin_id, userId);
    console.log('Jellyfin data received, Type:', jellyfinData.Type);
    console.log('MediaStreams available:', Boolean(jellyfinData.MediaStreams));
    
    // Then fetch from external sources based on media type
    let metadata = {
      resolution: this.extractResolution(jellyfinData),
      audioFormat: this.extractAudioFormat(jellyfinData),
      imdbRating: null,
      tmdbRating: null,
      metascore: null
    };

    // Fetch review scores for both Movies and Series
    if (jellyfinData.Type === 'Movie' || jellyfinData.Type === 'Series' || jellyfinData.Type === 'Episode') {
      const reviewData = await this.fetchReviewScores(item, jellyfinData, userId);
      metadata = { ...metadata, ...reviewData };
    }

    console.log('Final metadata:', metadata);
    
    // Cache the result
    this.cache.set(cacheKey, {
      data: metadata,
      timestamp: Date.now()
    });

    return metadata;
  }

  async fetchJellyfinData(jellyfinId, userId) {
    const settingsQuery = `
      SELECT jellyfin_url as url, jellyfin_api_key as token, jellyfin_user_id 
      FROM jellyfin_settings 
      WHERE user_id = $1
    `;
    
    const settingsResult = await db.query(settingsQuery, [userId]);
    const settings = settingsResult.rows[0];

    if (!settings) {
      throw new Error('Jellyfin settings not found');
    }

    // Clean up the URL - remove trailing slash if present
    const baseUrl = settings.url.replace(/\/$/, '');
    
    // Try the direct Items endpoint first (doesn't require user context)
    const itemUrl = `${baseUrl}/Items/${jellyfinId}`;
    // Fallback URL with user context
    const userItemUrl = `${baseUrl}/Users/${settings.jellyfin_user_id}/Items/${jellyfinId}`;

    console.log('Fetching Jellyfin data:', {
      url: itemUrl,
      token: settings.token ? '***' + settings.token.slice(-4) : 'none'
    });

    const headers = {
      'Accept': 'application/json'
    };

    // Add authorization header if token exists
    if (settings.token) {
      headers['X-Emby-Token'] = settings.token;
    }

    try {
      // Try the direct Items endpoint first
      let response = await fetch(itemUrl, {
        method: 'GET',
        headers: headers
      });

      // If that fails, try with user context
      if (!response.ok && response.status === 400) {
        console.log('Direct Items endpoint failed, trying with user context...');
        response = await fetch(userItemUrl, {
          method: 'GET',
          headers: headers
        });
      }

      if (!response.ok) {
        let errorBody = null;
        try {
          errorBody = await response.text();
        } catch (e) {
          // Ignore error reading body
        }
        
        console.error('Jellyfin API Error:', {
          status: response.status,
          statusText: response.statusText,
          url: itemUrl,
          headers: headers,
          errorBody: errorBody
        });
        throw new Error(`Failed to fetch Jellyfin data: ${response.status} ${response.statusText}` + (errorBody ? ` - ${errorBody}` : ''));
      }

      return response.json();
    } catch (error) {
      console.error('Error fetching from Jellyfin:', error);
      throw error;
    }
  }

  extractResolution(jellyfinData) {
    console.log('Extracting resolution from Jellyfin data');
    if (!jellyfinData.MediaStreams) {
      console.log('No MediaStreams found in Jellyfin data');
      return null;
    }

    const videoStream = jellyfinData.MediaStreams.find(s => s.Type === 'Video');
    if (!videoStream) {
      console.log('No video stream found');
      return null;
    }

    const width = videoStream.Width;
    const height = videoStream.Height;
    console.log(`Video dimensions: ${width}x${height}`);

    if (!width || !height) return null;

    // Determine resolution label
    if (width >= 7680) return '8K';
    if (width >= 3840) return '4K';
    if (width >= 2560) return '1440p';
    if (width >= 1920) return '1080p';
    if (width >= 1280) return '720p';
    if (width >= 854) return '480p';
    return 'SD';
  }

  extractAudioFormat(jellyfinData) {
    if (!jellyfinData.MediaStreams) return null;

    const audioStream = jellyfinData.MediaStreams.find(s => s.Type === 'Audio');
    if (!audioStream) return null;

    const codec = audioStream.Codec?.toLowerCase() || '';
    const channels = audioStream.Channels || 0;
    const profile = audioStream.Profile?.toLowerCase() || '';
    const format = audioStream.Format?.toLowerCase() || '';

    console.log('Audio stream info:', { codec, channels, profile, format });

    // Determine audio format with more specific mappings
    if (codec.includes('truehd') && profile.includes('atmos')) return 'truehd_atmos';
    if (codec.includes('eac3') && profile.includes('atmos')) return 'plus_atmos';
    if (codec.includes('dts') && profile.includes('x')) return 'dtsx';
    if (codec.includes('truehd')) return 'truehd';
    if (codec.includes('dts') && profile.includes('hd')) return 'dtses';
    if (codec.includes('dts')) return 'dts';
    if (codec.includes('eac3')) return 'plus';
    if (codec.includes('ac3')) return 'digital';
    if (codec.includes('aac')) return 'aac';
    if (codec.includes('mp3')) return 'mp3';
    if (codec.includes('flac')) return 'flac';
    if (codec.includes('opus')) return 'opus';
    if (codec.includes('vorbis')) return 'vorbis';
    if (codec.includes('pcm')) return 'pcm';
    
    // Default fallback based on channels
    return channels >= 6 ? `${channels} Channel` : 'Stereo';
  }

  async fetchReviewScores(item, jellyfinData, userId) {
    const scores = [];

    // Get API keys and enabled sources from database
    const apiKeysQuery = `
      SELECT 
        (SELECT api_key FROM tmdb_settings WHERE user_id = $1) as tmdb_key,
        (SELECT api_key FROM omdb_settings WHERE user_id = $1) as omdb_key,
        (SELECT username FROM anidb_settings WHERE user_id = $1) as anidb_username,
        (SELECT password FROM anidb_settings WHERE user_id = $1) as anidb_password
    `;
    
    const apiKeysResult = await db.query(apiKeysQuery, [userId]);
    const apiKeys = apiKeysResult.rows[0];

    // Get IDs from Jellyfin data
    const imdbId = jellyfinData.ProviderIds?.Imdb;
    const tmdbId = jellyfinData.ProviderIds?.Tmdb;
    const anidbId = jellyfinData.ProviderIds?.Anidb;

    // Fetch from TMDB
    if (tmdbId && apiKeys.tmdb_key) {
      try {
        const tmdbType = jellyfinData.Type === 'Movie' ? 'movie' : 'tv';
        const tmdbResponse = await fetch(
          `https://api.themoviedb.org/3/${tmdbType}/${tmdbId}?api_key=${apiKeys.tmdb_key}`
        );
        
        if (tmdbResponse.ok) {
          const tmdbData = await tmdbResponse.json();
          if (tmdbData.vote_average) {
            scores.push({
              name: 'TMDB',
              rating: tmdbData.vote_average.toFixed(1),
              outOf: 10
            });
          }
        }
      } catch (error) {
        console.error('Error fetching TMDB data:', error);
      }
    }

    // Fetch from OMDB (includes IMDb and Metacritic)
    if (imdbId && apiKeys.omdb_key) {
      try {
        const omdbResponse = await fetch(
          `http://www.omdbapi.com/?i=${imdbId}&apikey=${apiKeys.omdb_key}`
        );
        
        if (omdbResponse.ok) {
          const omdbData = await omdbResponse.json();
          
          // IMDb rating
          if (omdbData.imdbRating && omdbData.imdbRating !== 'N/A') {
            scores.push({
              name: 'IMDB',
              rating: parseFloat(omdbData.imdbRating).toFixed(1),
              outOf: 10
            });
          }
          
          // Metacritic score
          if (omdbData.Metascore && omdbData.Metascore !== 'N/A') {
            scores.push({
              name: 'Metacritic',
              rating: parseInt(omdbData.Metascore),
              outOf: 100
            });
          }
          
          // Rotten Tomatoes score
          if (omdbData.Ratings) {
            const rtRating = omdbData.Ratings.find(r => r.Source === 'Rotten Tomatoes');
            if (rtRating) {
              const rtScore = parseInt(rtRating.Value.replace('%', ''));
              scores.push({
                name: 'RT',
                rating: rtScore,
                outOf: 100
              });
            }
          }
        }
      } catch (error) {
        console.error('Error fetching OMDB data:', error);
      }
    }
    
    // Note: AniDB API integration would go here if implemented
    // Currently skipping AniDB as it requires XML parsing and authentication

    // For backwards compatibility, also set the first score as the legacy fields
    const result = {
      scores,
      // Legacy fields
      imdbRating: scores.find(s => s.name === 'IMDB')?.rating,
      tmdbRating: scores.find(s => s.name === 'TMDB')?.rating,
      metascore: scores.find(s => s.name === 'Metacritic')?.rating
    };

    console.log('Fetched review scores:', result);
    return result;
  }
}

export default MetadataService;
