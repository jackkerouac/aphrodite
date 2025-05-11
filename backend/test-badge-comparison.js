import { fileURLToPath } from 'url';
import path from 'path';
import fs from 'fs/promises';
import CanvasBadgeRenderer from './services/badge-renderer/canvasBadgeRenderer.js';
import { pool } from './db.js';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Our RATING_BG_COLOR_MAP and RATING_LOGO_MAP equivalent in backend
import { RATING_LOGO_MAP, RATING_BG_COLOR_MAP } from './services/badge-renderer/utils/logoMapping.js';

/**
 * Test script to analyze backend badge rendering
 */
async function testBadgeComparison() {
  try {
    console.log('Starting badge rendering comparison test...');
    
    // Initialize the badge renderer
    const renderer = new CanvasBadgeRenderer();
    await renderer.init();
    
    // Log backend branding maps
    console.log('Backend RATING_LOGO_MAP:', RATING_LOGO_MAP);
    console.log('Backend RATING_BG_COLOR_MAP:', RATING_BG_COLOR_MAP);
    
    // Create example review badge settings similar to what frontend would use
    const testReviewSettings = {
      type: 'review',
      size: 100,
      position: 'bottom-left',
      backgroundColor: '#000000',
      backgroundOpacity: 0.7,
      transparency: 0.7,
      borderRadius: 5,
      textColor: '#FFFFFF',
      fontSize: 14,
      displayFormat: 'vertical',
      maxSourcesToShow: 3,
      showDividers: true,
      useBrandColors: true, // This is important!
      // Sample review sources
      sources: [
        { name: 'IMDB', rating: 8.5, outOf: 10 },
        { name: 'RT', rating: 90, outOf: 100 },
        { name: 'Metacritic', rating: 75, outOf: 100 }
      ]
    };
    
    // Log the test settings
    console.log('Test review badge settings:', testReviewSettings);
    
    // Analyze how colors would be determined for each source
    testReviewSettings.sources.forEach(source => {
      analyzeSourceColors(source.name, testReviewSettings);
    });
    
    // Try to fetch actual settings from database if available
    try {
      const userId = 1; // Default user
      
      // Get review badge settings
      const reviewSettingsQuery = `
        SELECT *
        FROM review_badge_settings
        WHERE user_id = $1
      `;
      
      const reviewSettingsResult = await pool.query(reviewSettingsQuery, [userId]);
      if (reviewSettingsResult.rows.length > 0) {
        const dbSettings = reviewSettingsResult.rows[0];
        console.log('Database review badge settings:', dbSettings);
        
        // Check if the database has a useBrandColors field
        console.log('Does DB have useBrandColors field?', dbSettings.use_brand_colors !== undefined);
        
        // Try to map database settings to frontend-style settings
        const mappedSettings = {
          type: 'review',
          size: dbSettings.size,
          position: dbSettings.position,
          backgroundColor: dbSettings.background_color,
          backgroundOpacity: dbSettings.background_transparency || dbSettings.background_opacity,
          borderRadius: dbSettings.border_radius,
          textColor: dbSettings.text_color,
          fontSize: dbSettings.font_size,
          displayFormat: dbSettings.badge_layout || dbSettings.display_format || 'vertical',
          maxSourcesToShow: dbSettings.max_sources_to_show || 3,
          showDividers: dbSettings.show_dividers !== false,
          useBrandColors: dbSettings.use_brand_colors !== false
        };
        
        console.log('Mapped DB settings:', mappedSettings);
      }
    } catch (dbError) {
      console.log('Error fetching from database:', dbError.message);
      console.log('Continuing with test settings only...');
    }
    
    // Test rendering with Canvas using these settings
    console.log('Testing canvas rendering with settings...');
    const metadata = {
      rating: testReviewSettings.sources
    };
    
    const result = await renderer.renderReviewBadge(testReviewSettings, metadata);
    console.log('Rendering completed with dimensions:', result.width, 'x', result.height);
    
    // Save the result to a temp file for inspection
    const tempDir = path.join(__dirname, 'temp');
    try {
      await fs.mkdir(tempDir, { recursive: true });
    } catch (mkdirError) {
      console.error('Error creating temp directory:', mkdirError);
    }
    
    const outputPath = path.join(tempDir, 'test-review-badge.png');
    await fs.writeFile(outputPath, result);
    console.log(`Test badge saved to: ${outputPath}`);
    
    console.log('Badge rendering comparison test completed.');
  } catch (error) {
    console.error('Error running badge comparison test:', error);
  } finally {
    // Close the database pool
    if (pool) {
      await pool.end();
    }
  }
}

/**
 * Analyze how color would be determined for a given source
 */
function analyzeSourceColors(sourceName, settings) {
  const normalizedName = sourceName.toUpperCase();
  const hasBrandColor = RATING_BG_COLOR_MAP[normalizedName] !== undefined;
  const brandColor = RATING_BG_COLOR_MAP[normalizedName];
  const useBrandColors = settings.useBrandColors !== false;
  
  console.log(`Color analysis for ${sourceName}:`, {
    sourceName: normalizedName,
    hasBrandColor,
    brandColor,
    backgroundColor: settings.backgroundColor || '#000000',
    useBrandColors,
    effectiveColor: (useBrandColors && hasBrandColor) ? brandColor : settings.backgroundColor || '#000000'
  });
}

// Run the test
testBadgeComparison().catch(console.error);
