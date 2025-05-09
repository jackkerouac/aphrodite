/**
 * Load an image from a URL
 * @param url The URL of the image to load
 * @returns Promise resolving to an HTMLImageElement
 */
export async function loadImage(url: string): Promise<HTMLImageElement> {
  console.log(`Loading image from: ${url}`); // Add debug logging
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      console.log(`Successfully loaded image: ${url}`);
      resolve(img);
    };
    img.onerror = (e) => {
      console.error(`Failed to load image: ${url}`, e);
      reject(new Error(`Failed to load image: ${url}`));
    };
    img.src = url;
  });
}