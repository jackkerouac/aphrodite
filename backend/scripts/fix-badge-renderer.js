// Fix script for Aphrodite Badge Rendering System
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// Get current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define paths
const backendRoot = path.join(__dirname, '..');

async function fixAphrodite() {
  console.log('Starting Aphrodite Badge Rendering System fixes...');
  
  try {
    // 1. Run asset synchronization first
    console.log('Synchronizing assets...');
    const syncAssetsPath = path.join(backendRoot, 'services', 'unified-badge-renderer', 'syncAssets.js');
    
    // Check if the file exists, if not create it
    if (!fs.existsSync(syncAssetsPath)) {
      console.log('Creating asset synchronization script...');
      
      const syncAssetsContent = `// Asset synchronization script for Aphrodite Badge Rendering System
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

/**
 * Synchronize assets between frontend and backend
 * This ensures all badge icons are available for rendering
 */
async function syncAssets() {
  try {
    // Get path to the current script
    const __filename = fileURLToPath(import.meta.url);
    const __dirname = path.dirname(__filename);
    
    // Define paths
    const backendRoot = path.join(__dirname, '..', '..');
    const frontendRoot = path.join(backendRoot, '..');
    
    const backendAssets = path.join(backendRoot, 'public', 'assets');
    const frontendAssets = path.join(frontendRoot, 'src', 'assets');
    
    console.log('Starting asset synchronization...');
    console.log(\`Backend assets directory: \${backendAssets}\`);
    console.log(\`Frontend assets directory: \${frontendAssets}\`);
    
    // Ensure backend assets directory exists
    if (!fs.existsSync(backendAssets)) {
      fs.mkdirSync(backendAssets, { recursive: true });
      console.log(\`Created directory: \${backendAssets}\`);
    }
    
    // Define asset categories to sync
    const assetCategories = [
      {
        name: 'review_sources',
        ensureDirectory: true,
        sourceFiles: [
          { src: path.join(frontendAssets, 'imdb_logo.png'), dest: path.join(backendAssets, 'review_sources', 'imdb.png') },
          { src: path.join(frontendAssets, 'rt_logo.png'), dest: path.join(backendAssets, 'review_sources', 'rt_critics.png') },
          { src: path.join(frontendAssets, 'metacritic_logo.png'), dest: path.join(backendAssets, 'review_sources', 'metacritic.png') },
          { src: path.join(frontendAssets, 'tmdb_logo.png'), dest: path.join(backendAssets, 'review_sources', 'tmdb.png') }
        ]
      },
      {
        name: 'audio_codec',
        ensureDirectory: true,
        subDirs: ['compact'],
        recursive: true
      },
      {
        name: 'resolution',
        ensureDirectory: true,
        recursive: true
      }
    ];
    
    // Process each category
    for (const category of assetCategories) {
      const categoryBackendPath = path.join(backendAssets, category.name);
      
      // Create category directory if it doesn't exist
      if (category.ensureDirectory && !fs.existsSync(categoryBackendPath)) {
        fs.mkdirSync(categoryBackendPath, { recursive: true });
        console.log(\`Created directory: \${categoryBackendPath}\`);
      }
      
      // If category has specific files to copy
      if (category.sourceFiles) {
        for (const file of category.sourceFiles) {
          try {
            // Create parent directory if it doesn't exist
            const destDir = path.dirname(file.dest);
            if (!fs.existsSync(destDir)) {
              fs.mkdirSync(destDir, { recursive: true });
            }
            
            // Copy file if source exists
            if (fs.existsSync(file.src)) {
              fs.copyFileSync(file.src, file.dest);
              console.log(\`Copied: \${file.src} -> \${file.dest}\`);
            } else {
              console.warn(\`Source file not found: \${file.src}\`);
            }
          } catch (error) {
            console.error(\`Error copying \${file.src}: \${error.message}\`);
          }
        }
      }
      
      // If category has subdirectories to sync
      if (category.subDirs) {
        for (const subDir of category.subDirs) {
          const sourceDir = path.join(frontendAssets, category.name, subDir);
          const destDir = path.join(categoryBackendPath, subDir);
          
          // Create destination subdirectory if it doesn't exist
          if (!fs.existsSync(destDir)) {
            fs.mkdirSync(destDir, { recursive: true });
            console.log(\`Created directory: \${destDir}\`);
          }
          
          // Copy all files from source to destination
          if (fs.existsSync(sourceDir)) {
            const files = fs.readdirSync(sourceDir);
            
            for (const file of files) {
              const sourcePath = path.join(sourceDir, file);
              const destPath = path.join(destDir, file);
              
              // Only copy files, not directories
              if (fs.statSync(sourcePath).isFile()) {
                fs.copyFileSync(sourcePath, destPath);
                console.log(\`Copied: \${sourcePath} -> \${destPath}\`);
              }
            }
          } else {
            console.warn(\`Source directory not found: \${sourceDir}\`);
          }
        }
      }
      
      // If category should be recursively copied
      if (category.recursive) {
        const sourceCategoryDir = path.join(frontendAssets, category.name);
        
        // Check if source directory exists
        if (fs.existsSync(sourceCategoryDir)) {
          // Function to recursively copy files
          function copyRecursive(source, destination) {
            // Check if source is a directory
            if (fs.statSync(source).isDirectory()) {
              // Create destination directory if it doesn't exist
              if (!fs.existsSync(destination)) {
                fs.mkdirSync(destination, { recursive: true });
                console.log(\`Created directory: \${destination}\`);
              }
              
              // Get all files and directories in the source
              const items = fs.readdirSync(source);
              
              // Process each item
              for (const item of items) {
                const sourcePath = path.join(source, item);
                const destPath = path.join(destination, item);
                
                // Recursively copy if directory, otherwise copy file
                if (fs.statSync(sourcePath).isDirectory()) {
                  copyRecursive(sourcePath, destPath);
                } else {
                  fs.copyFileSync(sourcePath, destPath);
                  console.log(\`Copied: \${sourcePath} -> \${destPath}\`);
                }
              }
            } else {
              // If source is a file, just copy it
              fs.copyFileSync(source, destination);
              console.log(\`Copied: \${source} -> \${destination}\`);
            }
          }
          
          // Start recursive copy
          copyRecursive(sourceCategoryDir, categoryBackendPath);
        } else {
          console.warn(\`Source directory not found: \${sourceCategoryDir}\`);
        }
      }
    }
    
    console.log('Asset synchronization complete!');
    return true;
  } catch (error) {
    console.error(\`Error synchronizing assets: \${error.message}\`);
    return false;
  }
}

export default syncAssets;

// If this script is run directly, execute synchronization
if (process.argv[1] === fileURLToPath(import.meta.url)) {
  syncAssets().then(success => {
    if (success) {
      console.log('Asset synchronization completed successfully!');
      process.exit(0);
    } else {
      console.error('Asset synchronization failed!');
      process.exit(1);
    }
  });
}`;
      
      // Create the directory if it doesn't exist
      const syncAssetsDir = path.dirname(syncAssetsPath);
      if (!fs.existsSync(syncAssetsDir)) {
        fs.mkdirSync(syncAssetsDir, { recursive: true });
      }
      
      // Write the file
      fs.writeFileSync(syncAssetsPath, syncAssetsContent);
      console.log('Asset synchronization script created.');
    }
    
    // Run the script
    await execAsync(`node ${syncAssetsPath}`);
    console.log('Asset synchronization completed successfully.');
    
    // 2. Verify getReviewSourceIconPath function in nodeCanvasBadgeRenderer.js
    console.log('Verifying icon path function in nodeCanvasBadgeRenderer.js...');
    const canvasRendererPath = path.join(backendRoot, 'services', 'unified-badge-renderer', 'nodeCanvasBadgeRenderer.js');
    
    // Check if the file exists
    if (!fs.existsSync(canvasRendererPath)) {
      console.log('NodeCanvasBadgeRenderer.js not found, no changes needed.');
    } else {
      // Read the file content
      const canvasRendererContent = fs.readFileSync(canvasRendererPath, 'utf8');
      
      // Check if the improved function is already there
      if (canvasRendererContent.includes('sourceLower = source.toLowerCase()') && 
          canvasRendererContent.includes('possiblePaths = [')) {
        console.log('Improved icon path function already implemented, no changes needed.');
      } else {
        console.log('Installing improved icon path function...');
        
        const improvedFunction = `/**
 * Get the path to a review source icon with improved path handling
 * @param {string} source - Review source
 * @returns {Promise<string>} - Path to the icon
 */
async function getReviewSourceIconPath(source) {
  try {
    const sourceLower = source.toLowerCase();
    
    // Define all possible locations for this icon
    const possiblePaths = [
      // Primary location
      path.join(REVIEW_SOURCE_ICONS_DIR, \`\${sourceLower}.png\`),
      
      // Try with original case
      path.join(REVIEW_SOURCE_ICONS_DIR, \`\${source}.png\`),
      
      // Check for icons with _logo suffix
      path.join(REVIEW_SOURCE_ICONS_DIR, \`\${sourceLower}_logo.png\`),
      
      // Check source frontend assets
      path.join(process.cwd(), '..', 'src', 'assets', \`\${sourceLower}.png\`),
      path.join(process.cwd(), '..', 'src', 'assets', \`\${sourceLower}_logo.png\`),
      path.join(process.cwd(), '..', 'src', 'assets', \`\${source}_logo.png\`),
      
      // Special cases for specific source types
      ...(sourceLower === 'rt_critics' ? [
        path.join(REVIEW_SOURCE_ICONS_DIR, 'rt.png'),
        path.join(process.cwd(), '..', 'src', 'assets', 'rt_logo.png')
      ] : []),
      ...(sourceLower === 'imdb' ? [
        path.join(REVIEW_SOURCE_ICONS_DIR, 'imdb_logo.png'),
        path.join(process.cwd(), '..', 'src', 'assets', 'imdb_logo.png')
      ] : []),
      ...(sourceLower === 'metacritic' ? [
        path.join(REVIEW_SOURCE_ICONS_DIR, 'metacritic_logo.png'),
        path.join(process.cwd(), '..', 'src', 'assets', 'metacritic_logo.png')
      ] : []),
      ...(sourceLower === 'tmdb' ? [
        path.join(REVIEW_SOURCE_ICONS_DIR, 'tmdb_logo.png'),
        path.join(process.cwd(), '..', 'src', 'assets', 'tmdb_logo.png')
      ] : [])
    ];
    
    // Try each path in order
    for (const iconPath of possiblePaths) {
      try {
        await fs.access(iconPath);
        logger.info(\`Found icon for \${source} at \${iconPath}\`);
        return iconPath;
      } catch {
        // Path doesn't exist, continue to next one
        continue;
      }
    }
    
    // If we reach here, all paths failed
    // Try to create the directory if it doesn't exist
    try {
      await fs.mkdir(REVIEW_SOURCE_ICONS_DIR, { recursive: true });
    } catch (error) {
      // Ignore directory exists error
      if (error.code !== 'EEXIST') {
        logger.error(\`Error creating directory: \${error.message}\`);
      }
    }
    
    // Try to copy from frontend assets if available
    const potentialSources = [
      { src: path.join(process.cwd(), '..', 'src', 'assets', 'imdb_logo.png'), dest: path.join(REVIEW_SOURCE_ICONS_DIR, 'imdb.png') },
      { src: path.join(process.cwd(), '..', 'src', 'assets', 'rt_logo.png'), dest: path.join(REVIEW_SOURCE_ICONS_DIR, 'rt_critics.png') },
      { src: path.join(process.cwd(), '..', 'src', 'assets', 'metacritic_logo.png'), dest: path.join(REVIEW_SOURCE_ICONS_DIR, 'metacritic.png') },
      { src: path.join(process.cwd(), '..', 'src', 'assets', 'tmdb_logo.png'), dest: path.join(REVIEW_SOURCE_ICONS_DIR, 'tmdb.png') }
    ];
    
    // Try to copy each icon
    for (const { src, dest } of potentialSources) {
      try {
        // Check if source exists and destination doesn't
        await fs.access(src);
        
        try {
          await fs.access(dest);
        } catch {
          // Destination doesn't exist, copy the file
          const content = await fs.readFile(src);
          await fs.writeFile(dest, content);
          logger.info(\`Copied \${src} to \${dest}\`);
        }
      } catch (error) {
        logger.error(\`Error copying \${src}: \${error.message}\`);
      }
    }
    
    // After attempting to fix missing icons, try IMDB as fallback
    const imdbPath = path.join(REVIEW_SOURCE_ICONS_DIR, 'imdb.png');
    try {
      await fs.access(imdbPath);
      logger.warn(\`No icon found for \${source}, using IMDB fallback\`);
      return imdbPath;
    } catch {
      // Create an SVG placeholder for the missing icon
      const placeholderPath = path.join(REVIEW_SOURCE_ICONS_DIR, \`\${sourceLower}_placeholder.svg\`);
      
      // Create a simple SVG placeholder
      const svg = \`<svg width="100" height="50" xmlns="http://www.w3.org/2000/svg">
        <rect width="100" height="50" fill="#333"/>
        <text x="50" y="25" font-family="Arial" font-size="12" fill="white" text-anchor="middle" alignment-baseline="middle">\${source.toUpperCase()}</text>
      </svg>\`;
      
      await fs.writeFile(placeholderPath, svg);
      logger.warn(\`Created placeholder SVG for \${source} at \${placeholderPath}\`);
      
      return placeholderPath;
    }
  } catch (error) {
    logger.error(\`Error getting review source icon: \${error.message}\`);
    
    // Last resort - create an empty path that will trigger the text fallback
    return \`missing-\${source}.png\`;
  }
}`;
        
        // Find the function to replace
        const functionStartPattern = /async function getReviewSourceIconPath\(source\) {/;
        const functionEndPattern = /}/;
        
        // Find the start position
        const startPos = canvasRendererContent.search(functionStartPattern);
        if (startPos === -1) {
          console.warn('Could not find getReviewSourceIconPath function in nodeCanvasBadgeRenderer.js, no changes made.');
        } else {
          // Find the end position by counting braces
          let braceCount = 1;
          let endPos = canvasRendererContent.indexOf('{', startPos) + 1;
          while (braceCount > 0 && endPos < canvasRendererContent.length) {
            const char = canvasRendererContent.charAt(endPos);
            if (char === '{') braceCount++;
            if (char === '}') braceCount--;
            endPos++;
          }
          
          // Create new content
          const newContent = 
            canvasRendererContent.substring(0, startPos) + 
            improvedFunction + 
            canvasRendererContent.substring(endPos);
          
          // Write the updated file
          fs.writeFileSync(canvasRendererPath, newContent);
          console.log('Updated nodeCanvasBadgeRenderer.js with improved icon path handling.');
        }
      }
    }
    
    // 3. Create a test script to verify the fixes
    console.log('Creating test script...');
    const testScriptPath = path.join(backendRoot, 'tests', 'badge-renderer-test.js');
    
    // Make sure the tests directory exists
    if (!fs.existsSync(path.join(backendRoot, 'tests'))) {
      fs.mkdirSync(path.join(backendRoot, 'tests'), { recursive: true });
    }
    
    const testScriptContent = `
// Test script for badge rendering system
import { createCanvas } from 'canvas';
import path from 'path';
import fs from 'fs/promises';
import { fileURLToPath } from 'url';

// Get current directory
const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Import the functions to test
import { applyBadgesToPoster } from '../services/unified-badge-renderer/nodeCanvasBadgeRenderer.js';
import UnifiedPosterProcessor from '../services/unified-badge-renderer/unifiedPosterProcessor.js';

async function testBadgeRenderer() {
  console.log('Testing badge rendering system...');
  
  try {
    // Create a simple poster buffer for testing
    const canvas = createCanvas(1000, 1500);
    const ctx = canvas.getContext('2d');
    
    // Fill the canvas with a gradient background
    const gradient = ctx.createLinearGradient(0, 0, 1000, 1500);
    gradient.addColorStop(0, '#000033');
    gradient.addColorStop(1, '#003366');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, 1000, 1500);
    
    // Add some text to simulate a poster
    ctx.fillStyle = '#FFFFFF';
    ctx.font = 'bold 60px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('TEST POSTER', 500, 200);
    
    const posterBuffer = canvas.toBuffer('image/png');
    
    // Create some test badge settings
    const testBadges = [
      {
        badge_type: 'audio',
        badge_position: 'bottom-left',
        badge_size: 120,
        background_color: '#000000',
        background_opacity: 80,
        border_radius: 10,
        properties: {
          codec_type: 'dolby_atmos'
        }
      },
      {
        badge_type: 'resolution',
        badge_position: 'top-right',
        badge_size: 120,
        background_color: '#000000',
        background_opacity: 80,
        border_radius: 10,
        properties: {
          resolution_type: '4k'
        }
      },
      {
        badge_type: 'review',
        badge_position: 'bottom-right',
        badge_size: 120,
        background_color: '#000000',
        background_opacity: 80,
        border_radius: 10,
        display_format: 'vertical',
        properties: {
          review_sources: ['imdb', 'rt_critics', 'metacritic']
        },
        reviewScores: [
          { source: 'imdb', rating: 8.5, outOf: 10 },
          { source: 'rt_critics', rating: 85, outOf: 100 },
          { source: 'metacritic', rating: 75, outOf: 100 }
        ]
      }
    ];
    
    // Test applying badges
    const modifiedPosterBuffer = await applyBadgesToPoster(posterBuffer, testBadges);
    
    // Save the result
    const outputDir = path.join(__dirname, '..', 'temp');
    await fs.mkdir(outputDir, { recursive: true });
    const outputPath = path.join(outputDir, 'test-poster-with-badges.png');
    await fs.writeFile(outputPath, modifiedPosterBuffer);
    
    console.log(\`Test successful! Modified poster saved to \${outputPath}\`);
    return true;
  } catch (error) {
    console.error(\`Test failed: \${error.message}\`);
    return false;
  }
}

// Run the test
testBadgeRenderer().then(success => {
  if (success) {
    console.log('All tests passed!');
    process.exit(0);
  } else {
    console.error('Tests failed.');
    process.exit(1);
  }
});
`;
    
    fs.writeFileSync(testScriptPath, testScriptContent);
    console.log('Test script created successfully.');
    
    console.log('All fixes have been applied successfully!');
    
    return {
      success: true,
      message: 'All Aphrodite Badge Rendering System fixes have been applied successfully!'
    };
  } catch (error) {
    console.error(`Error applying fixes: ${error.message}`);
    return {
      success: false,
      message: `Fix application failed: ${error.message}`
    };
  }
}

// Run the fix script
fixAphrodite().then(result => {
  if (result.success) {
    console.log(result.message);
    console.log('\nRecommended actions:');
    console.log('1. Run the test script to verify the fixes: node backend/tests/badge-renderer-test.js');
    console.log('2. Restart the Aphrodite application to apply the changes');
    process.exit(0);
  } else {
    console.error(result.message);
    process.exit(1);
  }
});
