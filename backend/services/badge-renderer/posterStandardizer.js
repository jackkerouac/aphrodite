import sharp from 'sharp';
import { promises as fs } from 'fs';
import path from 'path';

class PosterStandardizer {
  constructor() {
    this.standardWidth = 1000; // Standard width for all posters
  }

  /**
   * Standardizes a poster to a consistent width while maintaining aspect ratio
   * @param {string} inputPath - Path to the original poster
   * @param {string} outputPath - Path where standardized poster will be saved
   * @returns {Promise<Object>} - Object containing the new dimensions
   */
  async standardizePoster(inputPath, outputPath) {
    try {
      console.log(`Standardizing poster from ${inputPath} to width ${this.standardWidth}px`);
      
      // Read the original poster
      const posterBuffer = await fs.readFile(inputPath);
      
      // Get metadata to calculate aspect ratio
      const metadata = await sharp(posterBuffer).metadata();
      const originalWidth = metadata.width;
      const originalHeight = metadata.height;
      
      // Calculate new height maintaining aspect ratio
      const aspectRatio = originalHeight / originalWidth;
      const newHeight = Math.round(this.standardWidth * aspectRatio);
      
      console.log(`Original dimensions: ${originalWidth}x${originalHeight}`);
      console.log(`Standardized dimensions: ${this.standardWidth}x${newHeight}`);
      
      // Resize the poster
      const standardizedBuffer = await sharp(posterBuffer)
        .resize(this.standardWidth, newHeight, {
          fit: 'fill',
          withoutEnlargement: false // Allow enlargement for smaller posters
        })
        .png() // Ensure output is PNG
        .toBuffer();
      
      // Save the standardized poster
      await fs.writeFile(outputPath, standardizedBuffer);
      
      return {
        originalWidth,
        originalHeight,
        newWidth: this.standardWidth,
        newHeight
      };
    } catch (error) {
      console.error('Error standardizing poster:', error);
      throw error;
    }
  }

  /**
   * Gets the standard width being used
   * @returns {number} The standard width in pixels
   */
  getStandardWidth() {
    return this.standardWidth;
  }
}

export default PosterStandardizer;
