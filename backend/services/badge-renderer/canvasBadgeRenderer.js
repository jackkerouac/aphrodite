import { createCanvas, registerFont } from 'canvas';
import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';

// Import the specialized renderers
import { renderAudioBadge } from './renderers/audioBadgeRenderer.js';
import { renderResolutionBadge } from './renderers/resolutionBadgeRenderer.js';
import { renderReviewBadge } from './renderers/reviewBadgeRenderer.js';

// Get project root path
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const projectRoot = path.resolve(__dirname, '../../..');

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
    
    // Handle different badge types
    switch (type) {
      case 'resolution':
        return await renderResolutionBadge(this.canvas, settings, metadata, sourceImagePath, this.fonts);
      case 'audio':
        return await renderAudioBadge(this.canvas, settings, metadata, sourceImagePath, this.fonts);
      case 'review':
        return await renderReviewBadge(this.canvas, settings, metadata, this.fonts);
      default:
        throw new Error(`Unsupported badge type: ${type}`);
    }
  }
}

export default CanvasBadgeRenderer;