import { createCanvas, registerFont } from 'canvas';
import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';

// Import the specialized renderers
import { renderAudioBadge } from './renderers/audioBadgeRenderer.js';
import { renderResolutionBadge } from './renderers/resolutionBadgeRenderer.js';
import { renderReviewBadge } from './renderers/reviewBadgeRenderer.js';

// Import utility functions
import { getAudioImagePath, getResolutionImagePath, projectRoot } from './utils/canvasUtils.js';

// Get project root path
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

/**
 * Canvas Badge Renderer
 * Manages rendering different types of badges for media items
 */
class CanvasBadgeRenderer {
  constructor() {
    console.log('CanvasBadgeRenderer initializing');
    this.loaded = false;
    this.fonts = new Map();
    this.canvas = createCanvas(200, 100); // Initial canvas size, will be resized as needed
  }

  /**
   * Initialize fonts and resources
   */
  async init() {
    if (this.loaded) return;
    
    // Load fonts - we'll load some default fonts
    try {
      const fontPath = path.join(projectRoot, 'src', 'assets', 'fonts');
      
      // Try to register some common fonts
      const fontFiles = {
        'Roboto': 'Roboto-Regular.ttf',
        'Roboto Bold': 'Roboto-Bold.ttf',
        'Inter': 'Inter-Regular.ttf',
        'Inter Bold': 'Inter-Bold.ttf'
      };

      for (const [fontName, fileName] of Object.entries(fontFiles)) {
        try {
          const fullPath = path.join(fontPath, fileName);
          const exists = await fs.access(fullPath).then(() => true).catch(() => false);
          
          if (exists) {
            registerFont(fullPath, { family: fontName });
            this.fonts.set(fontName, true);
            console.log(`Registered font: ${fontName}`);
          }
        } catch (err) {
          console.warn(`Failed to register font ${fontName}:`, err);
        }
      }
    } catch (err) {
      console.warn('Font loading failed:', err);
    }
    
    this.loaded = true;
  }

  /**
 * Render a badge based on its type
 * @param {string} type - The type of badge (resolution, audio, review)
 * @param {Object} settings - The badge settings
 * @param {Object} metadata - The metadata for the badge
 * @param {string} [sourceImagePath] - Optional path to an image to use
 * @returns {Promise<Buffer>} The rendered badge as a PNG buffer
 */
async renderBadge(type, settings, metadata, sourceImagePath) {
  await this.init();
  
  try {
    // Validate inputs
    if (!type) {
      throw new Error('Missing badge type');
    }
    
    if (!settings) {
      throw new Error('Missing badge settings');
    }
    
    // Make a copy of settings to avoid modifying the original
    const safeSettings = { ...settings };
    
    // Ensure size is valid
    if (safeSettings.size !== undefined) {
      // Guard against negative or invalid sizes
      if (typeof safeSettings.size !== 'number' || isNaN(safeSettings.size) || safeSettings.size <= 0) {
        console.warn(`Invalid badge size: ${safeSettings.size}, using default size 100`);
        safeSettings.size = 100; // Use default size if invalid
      }
    }
    
    // Handle different badge types
    switch (type.toLowerCase()) {
      case 'resolution':
        return await renderResolutionBadge(this.canvas, safeSettings, metadata || {}, sourceImagePath, this.fonts);
      case 'audio':
        return await renderAudioBadge(this.canvas, safeSettings, metadata || {}, sourceImagePath, this.fonts);
      case 'review':
        return await renderReviewBadge(this.canvas, safeSettings, metadata || {}, this.fonts);
      default:
        console.error(`Unsupported badge type: ${type}, defaulting to text badge`);
        // Create a fallback text badge
        const TextRenderer = await import('./renderers/audioBadgeRenderer.js');
        return TextRenderer.createFallbackBadge(this.canvas, `Unknown: ${type}`);
    }
  } catch (error) {
    console.error(`Error rendering badge type '${type}':`, error);
    try {
      // Attempt to create a fallback badge
      const TextRenderer = await import('./renderers/audioBadgeRenderer.js');
      return TextRenderer.createFallbackBadge(this.canvas, `Error: ${type}`);
    } catch (fallbackError) {
      // If even the fallback fails, create a transparent dummy image
      console.error('Failed to create fallback badge:', fallbackError);
      this.canvas.width = 100;
      this.canvas.height = 50;
      return this.canvas.toBuffer('image/png');
    }
  }
}
  
  /**
   * Map resolution values to asset paths - maintained for backward compatibility
   * @param {string} resolution - The resolution value
   * @returns {Promise<string|null>} The path to the resolution image, or null if not found
   */
  async getResolutionImagePath(resolution) {
    try {
      if (!resolution) {
        console.warn('Empty resolution value provided');
        return null;
      }
      
      return await getResolutionImagePath(resolution);
    } catch (error) {
      console.error(`Error finding resolution image path for '${resolution}':`, error);
      return null;
    }
  }
  
  /**
   * Map audio formats to asset paths - maintained for backward compatibility
   * @param {string} audioFormat - The audio format
   * @returns {Promise<string|null>} The path to the audio format image, or null if not found
   */
  async getAudioImagePath(audioFormat) {
    try {
      if (!audioFormat) {
        console.warn('Empty audio format provided');
        return null;
      }
      
      return await getAudioImagePath(audioFormat);
    } catch (error) {
      console.error(`Error finding audio format image path for '${audioFormat}':`, error);
      return null;
    }
  }
}

export default CanvasBadgeRenderer;