/**
 * Helper to preload images to ensure they're in browser cache
 */

// Images to preload
const imagesToPreload = [
  '/src/assets/example_poster_dark.jpg',
  '/src/assets/example_poster_light.jpg',
  '/src/assets/example_poster_dark.png',
  '/src/assets/example_poster_light.png'
];

/**
 * Preload all images in the list
 */
export const preloadImages = (): Promise<void[]> => {
  const promises = imagesToPreload.map(src => {
    return new Promise<void>((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        console.log(`Preloaded image: ${src}`);
        resolve();
      };
      img.onerror = (err) => {
        console.warn(`Failed to preload image: ${src}`, err);
        resolve(); // Resolve anyway to continue with other images
      };
      img.src = src;
    });
  });
  
  return Promise.all(promises);
};

/**
 * Initialize preloading immediately
 */
preloadImages().catch(err => {
  console.error('Error preloading images:', err);
});
