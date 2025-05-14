import { promises as fs } from 'fs';
import path from 'path';
import fetch from 'node-fetch';
import sharp from 'sharp';
import { pool as db } from '../../db.js';
import logger from '../../lib/logger.js';

/**
 * Simplified Poster Processor that uses the same approach as the Preview page
 * This processor directly uses the unified badge settings without transformation
 */
class UnifiedPosterProcessor {
  constructor() {
    this.tempDir = process.env.TEMP_DIR || path.join(process.cwd(), 'temp');
    console.log('UnifiedPosterProcessor initialized');
  }

  async init() {
    try {
      // Ensure temp directory exists
      await fs.mkdir(this.tempDir, { recursive: true });
      logger.info('UnifiedPosterProcessor: Temp directory created at ' + this.tempDir);
      
      // Import and run the asset synchronization script
      const syncAssets = (await import('./syncAssets.js')).default;
      await syncAssets();
      logger.info('UnifiedPosterProcessor: Assets synchronized successfully');
      
      return true;
    } catch (error) {
      logger.error(`Error initializing UnifiedPosterProcessor: ${error.message}`);
      // Continue initialization even if asset sync fails
      return true;
    }
  }

  /**
   * Process a single item
   * @param {Object} item - The job item to process
   * @param {number} jobId - The current job ID
   * @param {number} userId - The user ID
   * @returns {Promise<Object>} - Processing result
   */
  async processItem(item, jobId, userId) {
    const tempPosterPath = path.join(this.tempDir, `poster-${item.jellyfin_item_id}.png`);
    const standardizedPosterPath = path.join(this.tempDir, `poster-standardized-${item.jellyfin_item_id}.png`);
    const modifiedPosterPath = path.join(this.tempDir, `poster-modified-${item.jellyfin_item_id}.png`);
    
    try {
      // Step 1: Update item status to processing
      await this.updateItemStatus(item.id, 'processing');
      logger.info(`Job ${jobId}: Processing item ${item.id} (${item.jellyfin_item_id}: ${item.title || 'No title'})`);
      
      // Step 2: Validate input
      if (!item.jellyfin_item_id) {
        throw new Error('Missing jellyfin_item_id for item');
      }

      // Step 3: Fetch badge settings from unified_badge_settings table
      const badgeSettings = await this.fetchUnifiedBadgeSettings(userId, item.jellyfin_item_id);
      logger.info(`Job ${jobId}: Retrieved ${badgeSettings.length} badge settings for item ${item.id}`);
      // Log each badge type and position for debugging
      badgeSettings.forEach(badge => {
        logger.info(`Job ${jobId}: Badge type: ${badge.badge_type}, position: ${badge.badge_position}, size: ${badge.badge_size}`);
      });

      // Step 4: Download poster from Jellyfin
      await this.downloadPoster(item.jellyfin_item_id, tempPosterPath, userId);
      logger.info(`Job ${jobId}: Downloaded poster for item ${item.id}`);

      // Step 5: Standardize the poster to 1000px width
      const standardizationResult = await this.standardizePoster(tempPosterPath, standardizedPosterPath);
      logger.info(`Job ${jobId}: Standardized poster for item ${item.id}: ${JSON.stringify(standardizationResult)}`);

      // Step 6: Apply badges to the standardized poster
      // For now, we're mocking this part - in a real implementation, it would use Node Canvas to replicate
      // the browser-based badge rendering.
      let modifiedPosterBuffer = await this.applyBadgesToPoster(standardizedPosterPath, badgeSettings, item);
      
      // Step 7: Save the modified poster for inspection
      await fs.writeFile(modifiedPosterPath, modifiedPosterBuffer);
      logger.info(`Job ${jobId}: Modified poster saved at: ${modifiedPosterPath}`);

      // Step 8: Upload modified poster back to Jellyfin
      await this.uploadPoster(item.jellyfin_item_id, modifiedPosterBuffer, userId);
      logger.info(`Job ${jobId}: Uploaded modified poster for item ${item.id}`);

      // Step 9: Update item status to completed
      await this.updateItemStatus(item.id, 'completed');
      logger.info(`Job ${jobId}: Item ${item.id} completed successfully`);

      return { success: true, itemId: item.id };
    } catch (error) {
      logger.error(`Job ${jobId}: Error processing item ${item.id}: ${error.message}`);
      await this.updateItemStatus(item.id, 'failed', error.message);
      
      return { success: false, itemId: item.id, error: error.message };
    }
  }

  /**
   * Fetch unified badge settings for a specific user
   * @param {number} userId - The user ID
   * @param {string} jellyfinItemId - Optional Jellyfin item ID to get specific metadata
   * @returns {Promise<Array>} - Array of badge settings
   */
  async fetchUnifiedBadgeSettings(userId, jellyfinItemId) {
    try {
      const query = `
        SELECT *
        FROM unified_badge_settings
        WHERE user_id = $1
      `;
      
      const result = await db.query(query, [userId]);
      const settings = result.rows;
      
      // For each badge type, get the dynamic values from the Jellyfin metadata
      // This simulates what the frontend does but on the backend
      const resolvedSettings = await Promise.all(settings.map(async setting => {
        // Clone the setting to avoid modifying the original
        const resolvedSetting = { ...setting };
        
        // Add the dynamic values based on the badge type
        if (setting.badge_type === 'audio') {
          // Fetch audio codec from Jellyfin metadata
          const audioCodec = await this.getAudioCodecForItem(jellyfinItemId, userId);
          resolvedSetting.properties = { 
            ...(resolvedSetting.properties || {}),
            codec_type: audioCodec
          };
        } else if (setting.badge_type === 'resolution') {
          // Fetch resolution from Jellyfin metadata
          const resolution = await this.getResolutionForItem(jellyfinItemId, userId);
          resolvedSetting.properties = {
            ...(resolvedSetting.properties || {}),
            resolution_type: resolution
          };
        } else if (setting.badge_type === 'review') {
          // Fetch review data from Jellyfin metadata
          const reviewScores = await this.getReviewScoresForItem(jellyfinItemId, userId);
          resolvedSetting.properties = {
            ...(resolvedSetting.properties || {}),
            review_sources: reviewScores.map(s => s.source)
          };
          resolvedSetting.reviewScores = reviewScores;
        }
        
        return resolvedSetting;
      }));
      
      return resolvedSettings;
    } catch (error) {
      logger.error(`Error fetching unified badge settings: ${error.message}`);
      throw error;
    }
  }
  
  /**
   * Get audio codec information for an item
   * @param {string} jellyfinItemId - The Jellyfin item ID
   * @param {number} userId - The user ID
   * @returns {Promise<string>} - Audio codec type
   */
  async getAudioCodecForItem(jellyfinItemId, userId) {
    try {
      // Fetch item metadata from Jellyfin
      const metadata = await this.fetchJellyfinMetadata(jellyfinItemId, userId);
      
      // Extract audio codec information
      let audioCodec = 'dolby_atmos'; // Default
      
      if (metadata.MediaStreams) {
        // Look for audio streams
        const audioStreams = metadata.MediaStreams.filter(stream => stream.Type === 'Audio');
        
        if (audioStreams.length > 0) {
          // Use the first audio stream as the primary one
          const audioStream = audioStreams[0];
          
          // Map Jellyfin codec names to our recognized codec types
          const codecName = audioStream.Codec ? audioStream.Codec.toLowerCase() : '';
          
          if (codecName.includes('truehd') && (audioStream.Channels > 6 || audioStream.Channels === undefined)) {
            audioCodec = 'dolby_atmos';
          } else if (codecName.includes('truehd')) {
            audioCodec = 'dolby_truehd';
          } else if (codecName.includes('eac3') || codecName.includes('ac3') || codecName.includes('ac-3')) {
            if (audioStream.Channels > 6) {
              audioCodec = 'dolby_digital_plus';
            } else {
              audioCodec = 'dolby_digital';
            }
          } else if (codecName.includes('dts')) {
            if (codecName.includes('ma') || codecName.includes('master')) {
              audioCodec = 'dts_hd_ma';
            } else if (codecName.includes('hd')) {
              audioCodec = 'dts_hd';
            } else if (codecName.includes('x')) {
              audioCodec = 'dts_x';
            } else {
              audioCodec = 'dts';
            }
          } else if (codecName.includes('aac')) {
            audioCodec = 'aac';
          } else if (codecName.includes('mp3')) {
            audioCodec = 'mp3';
          } else if (codecName.includes('flac')) {
            audioCodec = 'flac';
          } else if (codecName.includes('pcm')) {
            audioCodec = 'pcm';
          } else if (codecName.includes('opus')) {
            audioCodec = 'opus';
          }
        }
      }
      
      logger.info(`Audio codec for ${jellyfinItemId}: ${audioCodec}`);
      return audioCodec;
    } catch (error) {
      logger.error(`Error getting audio codec: ${error.message}`);
      return 'dolby_atmos'; // Default fallback
    }
  }
  
  /**
   * Get resolution information for an item
   * @param {string} jellyfinItemId - The Jellyfin item ID
   * @param {number} userId - The user ID
   * @returns {Promise<string>} - Resolution type
   */
  async getResolutionForItem(jellyfinItemId, userId) {
    try {
      // Fetch item metadata from Jellyfin
      const metadata = await this.fetchJellyfinMetadata(jellyfinItemId, userId);
      
      // Extract resolution information
      let resolution = '4k'; // Default
      
      if (metadata.Width && metadata.Height) {
        const width = metadata.Width;
        
        // Determine resolution based on width
        if (width >= 3840) {
          resolution = '4k';
          
          // Check for HDR or Dolby Vision
          if (metadata.HasHdr === true) {
            resolution = '4khdr';
          }
          if (metadata.HasDolbyVision === true) {
            resolution = '4kdv';
          }
        } else if (width >= 1920) {
          resolution = '1080p';
          
          // Check for HDR or Dolby Vision
          if (metadata.HasHdr === true) {
            resolution = '1080phdr';
          }
          if (metadata.HasDolbyVision === true) {
            resolution = '1080pdv';
          }
        } else if (width >= 1280) {
          resolution = '720p';
          
          // Check for HDR
          if (metadata.HasHdr === true) {
            resolution = '720phdr';
          }
        } else if (width >= 720) {
          resolution = '576p';
        } else {
          resolution = '480p';
        }
      }
      
      logger.info(`Resolution for ${jellyfinItemId}: ${resolution}`);
      return resolution;
    } catch (error) {
      logger.error(`Error getting resolution: ${error.message}`);
      return '4k'; // Default fallback
    }
  }
  
  /**
   * Get review scores for an item
   * @param {string} jellyfinItemId - The Jellyfin item ID
   * @param {number} userId - The user ID
   * @returns {Promise<Array>} - Review scores
   */
  async getReviewScoresForItem(jellyfinItemId, userId) {
    try {
      // Fetch item metadata from Jellyfin
      const metadata = await this.fetchJellyfinMetadata(jellyfinItemId, userId);
      
      // Extract review scores
      const reviewScores = [];
      
      // First check if we have external IDs in the Jellyfin metadata
      const externalIds = metadata.ProviderIds || {};
      
      // Get IMDB ID - this is the primary key for most external APIs
      const imdbId = externalIds.Imdb;
      
      if (imdbId) {
        // Fetch data from OMDB API if we have an IMDB ID
        try {
          const omdbScores = await this.fetchOMDBRatings(imdbId, userId);
          reviewScores.push(...omdbScores);
        } catch (error) {
          logger.error(`Error fetching OMDB ratings: ${error.message}`);
          // Fall back to Jellyfin's community rating for IMDB
          if (metadata.CommunityRating) {
            reviewScores.push({
              source: 'imdb',
              rating: metadata.CommunityRating,
              outOf: 10
            });
          }
        }
      } else if (metadata.CommunityRating) {
        // If no IMDB ID but we have a community rating, use that for IMDB
        reviewScores.push({
          source: 'imdb',
          rating: metadata.CommunityRating,
          outOf: 10
        });
      }
      
      // Check for TMDB ID
      const tmdbId = externalIds.Tmdb;
      
      if (tmdbId) {
        // Fetch data from TMDB API
        try {
          const mediaType = metadata.Type === 'Movie' ? 'movie' : 'tv';
          const tmdbScore = await this.fetchTMDBRating(tmdbId, mediaType, userId);
          if (tmdbScore) {
            reviewScores.push(tmdbScore);
          }
        } catch (error) {
          logger.error(`Error fetching TMDB rating: ${error.message}`);
        }
      }
      
      // Check for Rotten Tomatoes ID
      if (externalIds.RottenTomatoes) {
        // Since direct RT API access requires a complex approval process,
        // we can use OMDB's RT data if we haven't already obtained it
        if (!reviewScores.some(score => score.source === 'rt_critics') && imdbId) {
          try {
            const rtScore = await this.fetchRottenTomatoesViaOMDB(imdbId, userId);
            if (rtScore) {
              reviewScores.push(rtScore);
            }
          } catch (error) {
            logger.error(`Error fetching RT rating: ${error.message}`);
            // Fallback to a placeholder
            reviewScores.push({
              source: 'rt_critics',
              rating: 75, // Placeholder
              outOf: 100
            });
          }
        }
      }
      
      // If no scores found, provide at least one placeholder
      if (reviewScores.length === 0) {
        reviewScores.push({
          source: 'imdb',
          rating: 7.5,
          outOf: 10
        });
      }
      
      logger.info(`Review scores for ${jellyfinItemId}: ${JSON.stringify(reviewScores)}`);
      return reviewScores;
    } catch (error) {
      logger.error(`Error getting review scores: ${error.message}`);
      return [{ source: 'imdb', rating: 7.5, outOf: 10 }]; // Default fallback
    }
  }
  
  /**
   * Fetch ratings from OMDB API
   * @param {string} imdbId - IMDB ID
   * @param {number} userId - User ID
   * @returns {Promise<Array>} - Array of review scores
   */
  async fetchOMDBRatings(imdbId, userId) {
    try {
      // Get OMDB API key from database
      const query = `SELECT api_key FROM omdb_settings WHERE user_id = $1`;
      const result = await db.query(query, [userId]);
      
      if (result.rows.length === 0 || !result.rows[0].api_key) {
        throw new Error('OMDB API key not found');
      }
      
      const apiKey = result.rows[0].api_key;
      const url = `https://www.omdbapi.com/?i=${imdbId}&apikey=${apiKey}`;
      
      logger.info(`Fetching OMDB data from ${url}`);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`OMDB API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.Error) {
        throw new Error(`OMDB API error: ${data.Error}`);
      }
      
      const reviewScores = [];
      
      // IMDB rating
      if (data.imdbRating && data.imdbRating !== 'N/A') {
        reviewScores.push({
          source: 'imdb',
          rating: parseFloat(data.imdbRating),
          outOf: 10
        });
      }
      
      return reviewScores;
    } catch (error) {
      logger.error(`Error fetching OMDB ratings: ${error.message}`);
      throw error;
    }
  }
  
  /**
   * Fetch Rotten Tomatoes rating via OMDB
   * @param {string} imdbId - IMDB ID
   * @param {number} userId - User ID
   * @returns {Promise<Object>} - Review score
   */
  async fetchRottenTomatoesViaOMDB(imdbId, userId) {
    try {
      // Get OMDB API key from database
      const query = `SELECT api_key FROM omdb_settings WHERE user_id = $1`;
      const result = await db.query(query, [userId]);
      
      if (result.rows.length === 0 || !result.rows[0].api_key) {
        throw new Error('OMDB API key not found');
      }
      
      const apiKey = result.rows[0].api_key;
      const url = `https://www.omdbapi.com/?i=${imdbId}&apikey=${apiKey}`;
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`OMDB API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.Error) {
        throw new Error(`OMDB API error: ${data.Error}`);
      }
      
      // Rotten Tomatoes ratings from OMDB
      if (data.Ratings) {
        const rtRating = data.Ratings.find(r => r.Source === 'Rotten Tomatoes');
        if (rtRating && rtRating.Value) {
          // Extract numeric value from percentage string (e.g., "75%")
          const match = rtRating.Value.match(/(\d+)%/);
          if (match && match[1]) {
            return {
              source: 'rt_critics',
              rating: parseInt(match[1]),
              outOf: 100
            };
          }
        }
      }
      
      return null;
    } catch (error) {
      logger.error(`Error fetching RT rating via OMDB: ${error.message}`);
      throw error;
    }
  }
  
  /**
   * Fetch rating from TMDB API
   * @param {string} tmdbId - TMDB ID
   * @param {string} mediaType - Media type (movie or tv)
   * @param {number} userId - User ID
   * @returns {Promise<Object>} - Review score
   */
  async fetchTMDBRating(tmdbId, mediaType, userId) {
    try {
      // Get TMDB API key from database
      const query = `SELECT api_key FROM tmdb_settings WHERE user_id = $1`;
      const result = await db.query(query, [userId]);
      
      if (result.rows.length === 0 || !result.rows[0].api_key) {
        throw new Error('TMDB API key not found');
      }
      
      const apiKey = result.rows[0].api_key;
      const url = `https://api.themoviedb.org/3/${mediaType}/${tmdbId}?api_key=${apiKey}`;
      
      logger.info(`Fetching TMDB data from ${url}`);
      
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`TMDB API error: ${response.status} ${response.statusText}`);
      }
      
      const data = await response.json();
      
      if (data.vote_average && data.vote_count > 0) {
        return {
          source: 'tmdb',
          rating: data.vote_average,
          outOf: 10
        };
      }
      
      return null;
    } catch (error) {
      logger.error(`Error fetching TMDB rating: ${error.message}`);
      throw error;
    }
  }
  
  /**
   * Fetch metadata from Jellyfin for a specific item
   * @param {string} jellyfinItemId - The Jellyfin item ID
   * @param {number} userId - The user ID
   * @returns {Promise<Object>} - Item metadata
   */
  async fetchJellyfinMetadata(jellyfinItemId, userId) {
    try {
      // Get Jellyfin settings from database
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
      
      // Clean up the URL by ensuring it has no trailing slash
      const baseUrl = settings.url.replace(/\/+$/, '');
      
      // Build the API URL for item info - URL format is important for Jellyfin API
      const apiUrl = `${baseUrl}/Items/${jellyfinItemId}?api_key=${settings.token}`;
      
      logger.info(`Fetching metadata from: ${apiUrl}`);
      
      // Fetch item data with proper error handling
      const response = await fetch(apiUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      if (!response.ok) {
        // Get error details for better debugging
        let errorDetails = '';
        try {
          const errorJson = await response.json();
          errorDetails = JSON.stringify(errorJson);
        } catch (e) {
          // If not JSON, try to get text
          errorDetails = await response.text();
        }
        
        logger.error(`Jellyfin API error: ${response.status} ${response.statusText}. Details: ${errorDetails}`);
        throw new Error(`Failed to fetch Jellyfin metadata: ${response.status} ${response.statusText}`);
      }
      
      const metadata = await response.json();
      
      // Log successful fetching
      logger.info(`Successfully fetched metadata for item ${jellyfinItemId}`);
      
      return metadata;
    } catch (error) {
      logger.error(`Error fetching Jellyfin metadata: ${error.message}`);
      
      // Provide more context in the error
      if (error.message.includes('Failed to fetch')) {
        throw new Error(`Jellyfin API error: ${error.message}. Please check your Jellyfin server URL and API key.`);
      }
      
      throw error;
    }
  }

  /**
   * Download poster from Jellyfin
   * @param {string} jellyfinId - The Jellyfin item ID
   * @param {string} outputPath - Path to save the poster
   * @param {number} userId - The user ID
   * @returns {Promise<void>}
   */
  async downloadPoster(jellyfinId, outputPath, userId) {
    // Get Jellyfin settings from database
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

    // Clean up the URL and build the poster URL
    const baseUrl = settings.url.replace(/\/$/, '');
    const posterUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary?api_key=${settings.token}`;
    
    logger.info(`Downloading poster: ${posterUrl}`);

    const response = await fetch(posterUrl);

    if (!response.ok) {
      throw new Error(`Failed to download poster: ${response.status} ${response.statusText}`);
    }

    const buffer = await response.buffer();
    await fs.writeFile(outputPath, buffer);
  }

  /**
   * Standardize poster to 1000px width while maintaining aspect ratio
   * @param {string} inputPath - Path to the input poster
   * @param {string} outputPath - Path to save the standardized poster
   * @returns {Promise<Object>} - Standardization result
   */
  async standardizePoster(inputPath, outputPath) {
    try {
      // Get image metadata
      const metadata = await sharp(inputPath).metadata();
      
      // Calculate new dimensions
      const targetWidth = 1000;
      const aspectRatio = metadata.height / metadata.width;
      const newHeight = Math.round(targetWidth * aspectRatio);
      
      // Resize the image
      await sharp(inputPath)
        .resize(targetWidth, newHeight)
        .png() // Convert to PNG to ensure consistent format
        .toFile(outputPath);
      
      return {
        originalWidth: metadata.width,
        originalHeight: metadata.height,
        newWidth: targetWidth,
        newHeight: newHeight,
        aspectRatio: aspectRatio
      };
    } catch (error) {
      logger.error(`Error standardizing poster: ${error.message}`);
      throw error;
    }
  }

  /**
   * Apply badges to a poster using our badge renderer
   * @param {string} posterPath - Path to the standardized poster
   * @param {Array} badges - Array of badge settings
   * @param {Object} item - The job item
   * @returns {Promise<Buffer>} - The modified poster buffer
   */
  async applyBadgesToPoster(posterPath, badges, item) {
    try {
      // Import the badge renderer module here - we're using the Node Canvas implementation
      const { applyBadgesToPoster } = await import('./nodeCanvasBadgeRenderer.js');
      
      // Read the poster file
      const posterBuffer = await fs.readFile(posterPath);
      
      // Apply the badges
      const modifiedPosterBuffer = await applyBadgesToPoster(posterBuffer, badges);
      
      return modifiedPosterBuffer;
    } catch (error) {
      logger.error(`Error applying badges to poster: ${error.message}`);
      throw error;
    }
  }

  /**
   * Upload poster to Jellyfin
   * @param {string} jellyfinId - The Jellyfin item ID
   * @param {Buffer} posterBuffer - The poster buffer
   * @param {number} userId - The user ID
   * @returns {Promise<void>}
   */
  async uploadPoster(jellyfinId, posterBuffer, userId) {
    // Get Jellyfin settings from database
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

    // Clean up the URL and build the upload URL
    const baseUrl = settings.url.replace(/\/$/, '');
    const uploadUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary?api_key=${settings.token}`;
    
    logger.info(`Uploading poster: ${uploadUrl}`);

    try {
      // First, try to delete existing image
      const deleteUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary?api_key=${settings.token}`;
      
      logger.info('Deleting existing image...');
      const deleteResponse = await fetch(deleteUrl, {
        method: 'DELETE'
      });
      logger.info(`Delete response: ${deleteResponse.status}`);
      
      // Now upload the new image
      logger.info('Uploading new poster...');
      const base64Data = posterBuffer.toString('base64');
      const response = await fetch(uploadUrl, {
        method: 'POST',
        headers: {
          'Content-Type': 'image/png',
          'Content-Encoding': 'base64'
        },
        body: base64Data
      });

      if (!response.ok) {
        // Try alternate approach with X-Emby-Token header
        logger.info('First attempt failed, trying with header authentication...');
        const headerUploadUrl = `${baseUrl}/Items/${jellyfinId}/Images/Primary`;
        
        const headerResponse = await fetch(headerUploadUrl, {
          method: 'POST',
          headers: {
            'X-Emby-Token': settings.token,
            'Content-Type': 'image/png',
            'Content-Encoding': 'base64'
          },
          body: base64Data
        });

        if (!headerResponse.ok) {
          throw new Error(`Failed to upload poster: Both methods failed. Last error: ${headerResponse.status} ${headerResponse.statusText}`);
        }
      }

      logger.info('Poster uploaded successfully!');
    } catch (error) {
      logger.error(`Error during poster upload: ${error.message}`);
      throw error;
    }
  }

  /**
   * Update the status of a job item
   * @param {number} itemId - The job item ID
   * @param {string} status - The new status
   * @param {string} errorMessage - Optional error message
   * @returns {Promise<void>}
   */
  async updateItemStatus(itemId, status, errorMessage = null) {
    const query = `
      UPDATE job_items 
      SET status = $1, 
          error_message = $2,
          updated_at = CURRENT_TIMESTAMP
      WHERE id = $3
    `;
    
    await db.query(query, [status, errorMessage, itemId]);
  }

  /**
   * Process items in batches
   * @param {Array} items - Array of job items
   * @param {number} jobId - The job ID
   * @param {number} userId - The user ID
   * @param {Function} onProgress - Progress callback
   * @returns {Promise<Array>} - Processing results
   */
  async processInBatches(items, jobId, userId, onProgress) {
    const results = [];
    const batchSize = parseInt(process.env.BATCH_SIZE || '4');
    
    logger.info(`Starting batch processing for job ${jobId} with ${items.length} items. Batch size: ${batchSize}`);
    
    for (let i = 0; i < items.length; i += batchSize) {
      const batch = items.slice(i, i + batchSize);
      const batchNumber = Math.floor(i / batchSize) + 1;
      const totalBatches = Math.ceil(items.length / batchSize);
      
      logger.info(`Processing batch ${batchNumber}/${totalBatches} with ${batch.length} items`);
      
      // Process batch in parallel
      const batchResults = await Promise.all(
        batch.map(item => this.processItem(item, jobId, userId))
      );
      
      results.push(...batchResults);
      
      // Report progress
      if (onProgress) {
        const completed = results.filter(r => r.success).length;
        const failed = results.filter(r => !r.success).length;
        const progress = (results.length / items.length) * 100;
        
        onProgress({
          completed,
          failed,
          total: items.length,
          progress: Math.round(progress)
        });
      }
    }
    
    logger.info(`Batch processing complete for job ${jobId}`);
    return results;
  }
}

export default UnifiedPosterProcessor;
