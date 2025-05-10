import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import logger from './logger.js';

// Get the directory name of the current module
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Docker-aware path configuration
const isDocker = process.env.IS_DOCKER === 'true';
const DATA_DIR = process.env.DATA_DIR || (isDocker ? '/app/data' : path.join(__dirname, '../../data'));
const TEMP_DIR = process.env.TEMP_DIR || (isDocker ? '/app/temp' : path.join(__dirname, '../../temp'));

// Ensure directories exist
[DATA_DIR, TEMP_DIR].forEach(dir => {
  try {
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
      logger.info(`Created directory: ${dir}`);
    }
  } catch (error) {
    logger.error(`Error creating directory ${dir}: ${error.message}`);
  }
});

/**
 * Get a Docker-aware path for file operations
 * @param {string} relativePath - The relative path within the data directory
 * @returns {string} The absolute path to use
 */
export function getDataPath(relativePath) {
  return path.join(DATA_DIR, relativePath);
}

/**
 * Get a temporary file path for processing
 * @param {string} filename - The filename to use
 * @returns {string} The absolute path to the temp file
 */
export function getTempPath(filename) {
  return path.join(TEMP_DIR, filename);
}

/**
 * Process an image with badge overlays
 * This is a placeholder for the actual image processing logic
 * In a real implementation, this would use libraries like Sharp or Canvas
 * 
 * @param {string} sourceImagePath - Path to the source image
 * @param {Object} badgeSettings - Badge settings to apply
 * @param {string} outputPath - Path to save the processed image
 * @returns {Promise<void>}
 */
export async function processImageWithBadges(sourceImagePath, badgeSettings, outputPath) {
  try {
    logger.info(`Processing image: ${sourceImagePath}`);
    logger.info(`Badge settings:`, badgeSettings);
    logger.info(`Output path: ${outputPath}`);
    
    // TODO: Implement actual image processing logic here
    // This would involve:
    // 1. Loading the source image
    // 2. Applying badges based on the settings
    // 3. Saving the result to the output path
    
    // For now, just copy the source to the output as a placeholder
    fs.copyFileSync(sourceImagePath, outputPath);
    
    logger.info(`Image processed successfully: ${outputPath}`);
  } catch (error) {
    logger.error(`Error processing image: ${error.message}`);
    throw error;
  }
}

/**
 * Download an image from a URL
 * @param {string} url - The URL to download from
 * @param {string} outputPath - Where to save the downloaded file
 * @returns {Promise<void>}
 */
export async function downloadImage(url, outputPath) {
  try {
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`Failed to download image: ${response.statusText}`);
    }
    
    const buffer = await response.arrayBuffer();
    fs.writeFileSync(outputPath, Buffer.from(buffer));
    
    logger.info(`Downloaded image: ${url} to ${outputPath}`);
  } catch (error) {
    logger.error(`Error downloading image: ${error.message}`);
    throw error;
  }
}

/**
 * Clean up temporary files
 * @param {string[]} filePaths - Array of file paths to clean up
 */
export function cleanupTempFiles(filePaths) {
  filePaths.forEach(filePath => {
    try {
      if (fs.existsSync(filePath)) {
        fs.unlinkSync(filePath);
        logger.info(`Cleaned up temp file: ${filePath}`);
      }
    } catch (error) {
      logger.error(`Error cleaning up file ${filePath}: ${error.message}`);
    }
  });
}
