/**
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
      path.join(REVIEW_SOURCE_ICONS_DIR, `${sourceLower}.png`),
      
      // Try with original case
      path.join(REVIEW_SOURCE_ICONS_DIR, `${source}.png`),
      
      // Check for icons with _logo suffix
      path.join(REVIEW_SOURCE_ICONS_DIR, `${sourceLower}_logo.png`),
      
      // Check source frontend assets
      path.join(process.cwd(), '..', 'src', 'assets', `${sourceLower}.png`),
      path.join(process.cwd(), '..', 'src', 'assets', `${sourceLower}_logo.png`),
      path.join(process.cwd(), '..', 'src', 'assets', `${source}_logo.png`),
      
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
        logger.info(`Found icon for ${source} at ${iconPath}`);
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
        logger.error(`Error creating directory: ${error.message}`);
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
          logger.info(`Copied ${src} to ${dest}`);
        }
      } catch (error) {
        logger.error(`Error copying ${src}: ${error.message}`);
      }
    }
    
    // After attempting to fix missing icons, try IMDB as fallback
    const imdbPath = path.join(REVIEW_SOURCE_ICONS_DIR, 'imdb.png');
    try {
      await fs.access(imdbPath);
      logger.warn(`No icon found for ${source}, using IMDB fallback`);
      return imdbPath;
    } catch {
      // Create an SVG placeholder for the missing icon
      const placeholderPath = path.join(REVIEW_SOURCE_ICONS_DIR, `${sourceLower}_placeholder.svg`);
      
      // Create a simple SVG placeholder
      const svg = `<svg width="100" height="50" xmlns="http://www.w3.org/2000/svg">
        <rect width="100" height="50" fill="#333"/>
        <text x="50" y="25" font-family="Arial" font-size="12" fill="white" text-anchor="middle" alignment-baseline="middle">${source.toUpperCase()}</text>
      </svg>`;
      
      await fs.writeFile(placeholderPath, svg);
      logger.warn(`Created placeholder SVG for ${source} at ${placeholderPath}`);
      
      return placeholderPath;
    }
  } catch (error) {
    logger.error(`Error getting review source icon: ${error.message}`);
    
    // Last resort - create an empty path that will trigger the text fallback
    return `missing-${source}.png`;
  }
}