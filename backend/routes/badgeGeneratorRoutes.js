import express from 'express';
import logger from '../lib/logger.js';

const router = express.Router();

// Utility function to extract the base64 image data from the frontend badge renderer
const generateBadgeBase64 = async (host, port, badgeData) => {
  try {
    const response = await fetch(`http://${host}:${port}/api/badge/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(badgeData)
    });

    if (!response.ok) {
      throw new Error(`Failed to generate badge: ${response.statusText}`);
    }

    const result = await response.json();
    return result.imageData;
  } catch (error) {
    logger.error('Error generating badge:', error);
    throw error;
  }
};

// Endpoint for generating badges using frontend renderer
router.post('/generate', async (req, res) => {
  try {
    const { type, settings, metadata } = req.body;
    
    if (!type || !settings) {
      return res.status(400).json({ error: 'Badge type and settings are required' });
    }

    logger.info(`Badge generation request received for type: ${type}`);
    
    // Map backend badge settings to frontend format
    const badgeOptions = {
      ...settings,
      // Map value based on type and metadata
      resolutionType: type === 'resolution' ? metadata?.resolution : undefined,
      audioType: type === 'audio' ? metadata?.audioFormat : undefined,
      rating: type === 'review' ? metadata?.rating : undefined,
      ratingType: type === 'review' ? (metadata?.ratingSource || 'imdb') : undefined,
      
      // Map visual settings
      backgroundColor: settings.backgroundColor || '#000000',
      backgroundOpacity: settings.transparency || 1,
      borderColor: settings.borderColor || '#FFFFFF',
      borderWidth: settings.borderWidth || 0,
      borderOpacity: settings.borderOpacity || 1,
      borderRadius: settings.borderRadius || 0,
      shadowEnabled: settings.shadowEnabled || false,
      shadowColor: settings.shadowColor || '#000000',
      shadowBlur: settings.shadowBlur || 5,
      shadowOffsetX: settings.shadowOffsetX || 0,
      shadowOffsetY: settings.shadowOffsetY || 0,
      textColor: settings.textColor || '#FFFFFF',
      fontSize: settings.fontSize || 14,
      fontFamily: settings.fontFamily || 'Arial',
      margin: settings.padding || 8,
      size: 100 // Default size for badges
    };

    // Determine the source image URL based on metadata and badge type
    let sourceImageUrl = null;
    
    if (type === 'resolution' && metadata?.resolution) {
      // Map resolution to image file
      const resolutionMap = {
        '8K': 'src/assets/resolution/8k.png',
        '4K': 'src/assets/resolution/4k.png',
        '1440p': 'src/assets/resolution/1440p.png',
        '1080p': 'src/assets/resolution/1080p.png',
        '720p': 'src/assets/resolution/720p.png',
        '480p': 'src/assets/resolution/480p.png',
        'SD': 'src/assets/resolution/sd.png'
      };
      sourceImageUrl = resolutionMap[metadata.resolution];
    } else if (type === 'audio' && metadata?.audioFormat) {
      // Map audio format to image file
      // The audio format from metadata will need to be mapped to appropriate image
      sourceImageUrl = `src/assets/audio_codec/standard/${metadata.audioFormat.toLowerCase().replace(/\s+/g, '_')}.png`;
    }

    // Use the frontend host and port for badge generation
    const frontendHost = process.env.FRONTEND_HOST || 'localhost';
    const frontendPort = process.env.FRONTEND_PORT || '5173';
    
    const frontendData = {
      type,
      options: badgeOptions,
      sourceImageUrl
    };

    // Since we can't directly call the frontend from backend, we'll implement the badge generation here
    // For now, return a simple response structure that the posterProcessor can use
    const badgeData = {
      type,
      settings: badgeOptions,
      sourceImageUrl,
      metadata
    };

    res.json({ 
      success: true,
      badgeData
    });

  } catch (error) {
    logger.error('Error in badge generation:', error);
    res.status(500).json({ error: error.message });
  }
});

export default router;
