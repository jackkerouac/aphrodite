// Use a WeakMap to prevent memory leaks with image caching
const posterCache = new WeakMap();
// Cache for dimensions by URL
const dimensionsCache: { [key: string]: PosterDimensions } = {};
export interface PosterDimensions {
  width: number;
  height: number;
  aspectRatio: number;
}

export const resizePoster = (
  originalUrl: string, 
  targetWidth: number = 1000
): Promise<{url: string, dimensions: PosterDimensions}> => {
  // Create a cache key
  const cacheKey = `${originalUrl}_${targetWidth}`;
  
  // Check if we have cached dimensions
  if (dimensionsCache[cacheKey]) {
    return Promise.resolve({
      url: originalUrl,
      dimensions: dimensionsCache[cacheKey]
    });
  }

  return new Promise((resolve, reject) => {
    try {
      const img = new Image();
      img.crossOrigin = "anonymous";
      
      // Set up a timeout to prevent infinite loading
      const loadTimeout = setTimeout(() => {
        reject(new Error('Poster loading timed out'));
      }, 10000); // 10 second timeout
      
      img.onload = () => {
        clearTimeout(loadTimeout);
        
        // Calculate dimensions while maintaining aspect ratio
        const height = (img.height / img.width) * targetWidth;
        const dimensions = {
          width: targetWidth,
          height: height,
          aspectRatio: img.width / img.height,
        };
        
        // Cache the dimensions
        dimensionsCache[cacheKey] = dimensions;
        
        // Cache the image instance in the WeakMap
        posterCache.set(img, dimensions);
        
        resolve({ url: originalUrl, dimensions: dimensions });
      };
      
      img.onerror = () => {
        clearTimeout(loadTimeout);
        reject(new Error(`Failed to load image: ${originalUrl}`));
      };
      
      img.src = originalUrl;
    } catch (error) {
      reject(error);
    }
  });
};

export const calculateBadgePosition = (
  posterDimensions: PosterDimensions,
  badgePosition: {x: number, y: number, percentX?: number, percentY?: number}
): {x: number, y: number, percentX: number, percentY: number} => {
  // Convert between absolute and percentage positions
  let percentX = badgePosition.percentX !== undefined ? badgePosition.percentX : 0;
  let percentY = badgePosition.percentY !== undefined ? badgePosition.percentY : 0;

  if (badgePosition.x !== undefined && badgePosition.y !== undefined) {
    percentX = (badgePosition.x / posterDimensions.width) * 100;
    percentY = (badgePosition.y / posterDimensions.height) * 100;
  }

  return {
    x: badgePosition.x || (percentX / 100) * posterDimensions.width,
    y: badgePosition.y || (percentY / 100) * posterDimensions.height,
    percentX: badgePosition.x !== undefined ? (badgePosition.x / posterDimensions.width) * 100 : percentX,
    percentY: badgePosition.y !== undefined ? (badgePosition.y / posterDimensions.height) * 100 : percentY,
  };
};