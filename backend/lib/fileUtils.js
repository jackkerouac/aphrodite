import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './logger.js';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Path to the badges directory
const BADGES_DIR = path.join(__dirname, '..', 'public', 'badges');

// Ensure the badges directory exists
try {
  if (!fs.existsSync(BADGES_DIR)) {
    fs.mkdirSync(BADGES_DIR, { recursive: true });
    logger.info(`Created badges directory at ${BADGES_DIR}`);
  }
} catch (error) {
  logger.error(`Error ensuring badges directory exists: ${error.message}`);
}

/**
 * Save a Base64 image to the badges directory
 * 
 * @param {string} base64Data Base64-encoded image data (can include the data URI prefix)
 * @param {string} userId User ID
 * @param {string} badgeType Type of badge (e.g., 'audio', 'resolution', 'review')
 * @returns {string} File path relative to the public directory (for use in URLs)
 */
export const saveBadgeImage = (base64Data, userId, badgeType) => {
  try {
    logger.info(`Attempting to save badge image. Data length: ${base64Data ? base64Data.length : 0} chars`);
    
    // Check if we actually received data
    if (!base64Data) {
      logger.error('No base64Data provided to saveBadgeImage');
      return null;
    }
    // Extract the base64 data from the data URI if present
    let imageData = base64Data;
    if (base64Data.startsWith('data:')) {
      logger.info('Base64 data starts with data: URI prefix, extracting actual data');
      const matches = base64Data.match(/^data:([A-Za-z-+/]+);base64,(.+)$/);
      if (matches && matches.length === 3) {
        imageData = matches[2];
        logger.info(`Extracted base64 data. MIME type: ${matches[1]}, Data length: ${imageData.length} chars`);
      } else {
        logger.error('Invalid Base64 data URI format');
        throw new Error('Invalid Base64 data URI format');
      }
    }
    
    // Create a unique filename based on user ID, badge type, and timestamp
    const timestamp = new Date().getTime();
    const filename = `${userId}_${badgeType}_${timestamp}.png`;
    const filepath = path.join(BADGES_DIR, filename);
    
    // Log some debugging info
    logger.info(`Writing to file: ${filepath}`);
    
    // Convert Base64 to binary and save to file
    fs.writeFileSync(filepath, Buffer.from(imageData, 'base64'));
    
    logger.info(`Successfully saved badge image: ${filename}, size: ${fs.statSync(filepath).size} bytes`);
    
    // Return the relative path for use in URLs
    return `/badges/${filename}`;
  } catch (error) {
    logger.error(`Error saving badge image: ${error.message}`);
    throw error;
  }
};

/**
 * Delete a badge image file
 * 
 * @param {string} filename Name of the file to delete (just the filename, not the full path)
 * @returns {boolean} True if the file was deleted, false otherwise
 */
export const deleteBadgeImage = (filename) => {
  try {
    const filepath = path.join(BADGES_DIR, path.basename(filename));
    
    if (fs.existsSync(filepath)) {
      fs.unlinkSync(filepath);
      logger.info(`Deleted badge image: ${filename}`);
      return true;
    } else {
      logger.warn(`Badge image not found: ${filename}`);
      return false;
    }
  } catch (error) {
    logger.error(`Error deleting badge image: ${error.message}`);
    return false;
  }
};
