import express from 'express';
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from '../lib/logger.js';

const router = express.Router();

// Get the directory name based on ES modules
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define the directory where badge files will be stored
const badgeFilesDir = path.join(__dirname, '../', 'storage', 'badges');

// Ensure the directory exists
if (!fs.existsSync(badgeFilesDir)) {
  try {
    fs.mkdirSync(badgeFilesDir, { recursive: true });
    logger.info(`Created badges directory at: ${badgeFilesDir}`);
  } catch (error) {
    logger.error(`Error creating badges directory: ${error.message}`);
  }
}

logger.info(`Badge files will be stored in: ${badgeFilesDir}`);

/**
 * @route POST /api/badge-files/:userId/:type
 * @description Saves a badge image to the server
 */
router.post('/:userId/:type', async (req, res) => {
  logger.info(`Received request to save badge file: ${req.params.type} for user ${req.params.userId}`);
  
  const { userId, type } = req.params;
  const { imageData } = req.body;
  
  if (!imageData) {
    logger.error('No image data provided');
    return res.status(400).json({ message: 'No image data provided' });
  }
  
  logger.info(`Image data received, length: ${imageData.length} characters`);
  
  try {
    // Create user directory if it doesn't exist
    const userDir = path.join(badgeFilesDir, userId);
    logger.info(`User directory path: ${userDir}`);
    
    if (!fs.existsSync(userDir)) {
      logger.info(`Creating user directory: ${userDir}`);
      fs.mkdirSync(userDir, { recursive: true });
    }
    
    // Convert base64 data to binary
    const base64Data = imageData.replace(/^data:image\/png;base64,/, '');
    const fileName = `${type}-badge.png`;
    const filePath = path.join(userDir, fileName);
    
    logger.info(`Writing file to: ${filePath}`);
    
    // Write the file
    fs.writeFileSync(filePath, base64Data, 'base64');
    logger.info(`Successfully saved ${type} badge for user ${userId} at: ${filePath}`);
    
    res.json({ 
      message: 'Badge file saved successfully',
      path: filePath,
      fileName
    });
  } catch (error) {
    logger.error(`Error saving badge file: ${error.message}`);
    logger.error(error.stack);
    res.status(500).json({ 
      message: 'Server error', 
      error: error.message,
      stack: error.stack
    });
  }
});

// Add a test route to verify the endpoint is accessible
router.get('/test', (req, res) => {
  logger.info('Badge files test route accessed');
  res.json({ 
    message: 'Badge files API is working', 
    storageDir: badgeFilesDir 
  });
});

export default router;
