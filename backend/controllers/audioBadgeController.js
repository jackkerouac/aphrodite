import {
  getAudioBadgeSettingsByUserId,
  upsertAudioBadgeSettings
} from '../models/audioBadgeSettings.js';
import { generateAudioBadge } from '../utils/badgeGenerator.js';
import logger from '../lib/logger.js';

/**
 * Get audio badge settings for a user
 */
export const getSettings = async (req, res) => {
  const userId = Number(req.params.userId);
  logger.info(`Getting audio badge settings for user ID: ${userId}`);
  
  try {
    const settings = await getAudioBadgeSettingsByUserId(userId);
    
    if (!settings) {
      logger.info(`No audio badge settings found for user ID: ${userId}`);
      return res.status(404).json({ message: 'Settings not found' });
    }
    
    // Don't send the badge image in the settings response to reduce payload size
    const { badge_image, ...settingsWithoutImage } = settings;
    
    logger.info(`Returning audio badge settings for user ID: ${userId}`);
    res.json(settingsWithoutImage);
  } catch (error) {
    logger.error(`Error getting audio badge settings: ${error.message}`);
    res.status(500).json({ message: 'Server error' });
  }
};

/**
 * Save or update audio badge settings for a user
 */
export const saveSettings = async (req, res) => {
  const userId = Number(req.params.userId);
  logger.info(`Saving audio badge settings for user ID: ${userId}`);
  
  try {
    // Extract fields from request body
    const { 
      size, 
      margin, 
      position,
      audio_codec_type,
      background_color, 
      background_transparency,
      border_radius,
      border_width,
      border_color,
      border_transparency,
      shadow_toggle,
      shadow_color,
      shadow_blur_radius,
      shadow_offset_x,
      shadow_offset_y,
      z_index
    } = req.body;
    
    // Check if there's a badge image in the request
    const badge_image = req.file ? req.file.buffer : null;
    
    // If there's a base64 encoded image in the request body, use that
    const badge_image_base64 = req.body.badge_image_base64;
    let processedBadgeImage = badge_image;
    
    if (!badge_image && badge_image_base64) {
      try {
        // Remove data URL prefix if it exists
        const base64Data = badge_image_base64.replace(/^data:image\\/(png|jpeg|jpg|svg\\+xml);base64,/, '');
        processedBadgeImage = Buffer.from(base64Data, 'base64');
        logger.info('Badge image processed from base64 data');
      } catch (error) {
        logger.error(`Error processing base64 image: ${error.message}`);
        return res.status(400).json({ message: 'Invalid base64 image data' });
      }
    }
    
    // If no image is provided, generate one based on settings
    if (!processedBadgeImage) {
      try {
        processedBadgeImage = await generateAudioBadge({
          size,
          margin,
          position,
          audio_codec_type,
          background_color,
          background_transparency,
          border_radius,
          border_width,
          border_color,
          border_transparency,
          shadow_toggle,
          shadow_color,
          shadow_blur_radius,
          shadow_offset_x,
          shadow_offset_y,
          z_index
        });
        logger.info('Generated audio badge image from settings');
      } catch (error) {
        logger.error(`Error generating audio badge image: ${error.message}`);
        // Continue without image if generation fails
      }
    }
    
    // Validate required fields
    const missingFields = [];
    
    if (size === undefined) missingFields.push('size');
    if (margin === undefined) missingFields.push('margin');
    if (!position) missingFields.push('position');
    if (!audio_codec_type) missingFields.push('audio_codec_type');
    if (!background_color) missingFields.push('background_color');
    if (background_transparency === undefined) missingFields.push('background_transparency');
    if (border_radius === undefined) missingFields.push('border_radius');
    if (border_width === undefined) missingFields.push('border_width');
    if (!border_color) missingFields.push('border_color');
    if (border_transparency === undefined) missingFields.push('border_transparency');
    if (z_index === undefined) missingFields.push('z_index');
    
    if (missingFields.length > 0) {
      const errorMessage = `Missing required fields: ${missingFields.join(', ')}`;
      logger.warn(errorMessage);
      return res.status(400).json({ message: errorMessage });
    }
    
    // Save settings to database
    const saved = await upsertAudioBadgeSettings({
      user_id: userId,
      size,
      margin,
      position,
      audio_codec_type,
      background_color,
      background_transparency,
      border_radius,
      border_width,
      border_color,
      border_transparency,
      shadow_toggle,
      shadow_color,
      shadow_blur_radius,
      shadow_offset_x,
      shadow_offset_y,
      z_index,
      badge_image: processedBadgeImage
    });
    
    // Don't send the badge image in the response to reduce payload size
    const { badge_image: savedImage, ...savedWithoutImage } = saved;
    
    logger.info(`Audio badge settings saved successfully for user ID: ${userId}`);
    res.json(savedWithoutImage);
  } catch (error) {
    logger.error(`Error saving audio badge settings: ${error.message}`);
    res.status(500).json({ message: 'Server error' });
  }
};

/**
 * Get the badge image for a user
 */
export const getBadgeImage = async (req, res) => {
  const userId = Number(req.params.userId);
  logger.info(`Getting audio badge image for user ID: ${userId}`);
  
  try {
    const settings = await getAudioBadgeSettingsByUserId(userId);
    
    if (!settings || !settings.badge_image) {
      logger.info(`No badge image found for user ID: ${userId}`);
      
      // If settings exist but no image, generate one on the fly
      if (settings) {
        try {
          const generatedImage = await generateAudioBadge(settings);
          
          // Set content type header and send the image data
          res.setHeader('Content-Type', 'image/png');
          res.send(generatedImage);
          
          // Update the settings with the generated image for future use
          await upsertAudioBadgeSettings({
            ...settings,
            badge_image: generatedImage
          });
          
          return;
        } catch (genError) {
          logger.error(`Error generating badge image on the fly: ${genError.message}`);
          // Fall through to 404 if generation fails
        }
      }
      
      return res.status(404).json({ message: 'Badge image not found' });
    }
    
    // Set content type header and send the image data
    res.setHeader('Content-Type', 'image/png');
    res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    res.setHeader('Pragma', 'no-cache');
    res.setHeader('Expires', '0');
    res.send(settings.badge_image);
  } catch (error) {
    logger.error(`Error getting audio badge image: ${error.message}`);
    res.status(500).json({ message: 'Server error' });
  }
};