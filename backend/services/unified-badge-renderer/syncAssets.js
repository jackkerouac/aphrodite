// Asset synchronization script for Aphrodite Badge Rendering System
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
    console.log(`Backend assets directory: ${backendAssets}`);
    console.log(`Frontend assets directory: ${frontendAssets}`);
    
    // Ensure backend assets directory exists
    if (!fs.existsSync(backendAssets)) {
      fs.mkdirSync(backendAssets, { recursive: true });
      console.log(`Created directory: ${backendAssets}`);
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
        console.log(`Created directory: ${categoryBackendPath}`);
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
              console.log(`Copied: ${file.src} -> ${file.dest}`);
            } else {
              console.warn(`Source file not found: ${file.src}`);
            }
          } catch (error) {
            console.error(`Error copying ${file.src}: ${error.message}`);
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
            console.log(`Created directory: ${destDir}`);
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
                console.log(`Copied: ${sourcePath} -> ${destPath}`);
              }
            }
          } else {
            console.warn(`Source directory not found: ${sourceDir}`);
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
                console.log(`Created directory: ${destination}`);
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
                  console.log(`Copied: ${sourcePath} -> ${destPath}`);
                }
              }
            } else {
              // If source is a file, just copy it
              fs.copyFileSync(source, destination);
              console.log(`Copied: ${source} -> ${destination}`);
            }
          }
          
          // Start recursive copy
          copyRecursive(sourceCategoryDir, categoryBackendPath);
        } else {
          console.warn(`Source directory not found: ${sourceCategoryDir}`);
        }
      }
    }
    
    console.log('Asset synchronization complete!');
    return true;
  } catch (error) {
    console.error(`Error synchronizing assets: ${error.message}`);
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
}
