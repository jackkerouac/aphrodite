/**
 * Utility functions for capturing badge images
 */

/**
 * Captures a badge as a Base64 image string
 * 
 * @param badgeImageSrc Source URL of the badge image
 * @param settings Badge display settings
 * @returns Promise resolving to a Base64 encoded string of the badge image
 */
export const captureBadgeAsBase64 = async (
  badgeImageSrc: string,
  settings: {
    size: number;
    background_color: string;
    background_transparency: number;
    border_radius: number;
    border_width: number;
    border_color: string;
    border_transparency: number;
    shadow_toggle: boolean;
    shadow_color: string;
    shadow_blur_radius: number;
    shadow_offset_x: number;
    shadow_offset_y: number;
  }
): Promise<string> => {
  console.log('🎨 [imageCaptureUtil] Capturing badge as base64, source:', badgeImageSrc);
  console.log('🎨 [imageCaptureUtil] Using settings:', settings);
  return new Promise((resolve, reject) => {
    // Create a new image to load the badge
    const img = new Image();
    
    // For debugging, add event listeners first
    img.onload = () => {
      console.log('✅ [imageCaptureUtil] Image loaded successfully:', img.src, `${img.naturalWidth}x${img.naturalHeight}`);
      
      try {
        // Create a canvas to draw the badge with its styling
        const canvas = document.createElement('canvas');
        // Set canvas size to accommodate shadow and border
        const padding = 20; // Extra padding for shadow and border
        canvas.width = img.naturalWidth * (settings.size / 100) + padding * 2;
        canvas.height = img.naturalHeight * (settings.size / 100) + padding * 2;
        
        console.log('🏞️ [imageCaptureUtil] Created canvas:', `${canvas.width}x${canvas.height}`);
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Could not get canvas context'));
          return;
        }
        
        // Start with a transparent canvas
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        
        // Calculate center position for the badge
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        
        // Apply shadow if enabled
        if (settings.shadow_toggle) {
          ctx.shadowOffsetX = settings.shadow_offset_x;
          ctx.shadowOffsetY = settings.shadow_offset_y;
          ctx.shadowBlur = settings.shadow_blur_radius;
          
          // Convert hex to rgba for shadow
          const r = parseInt(settings.shadow_color.slice(1, 3), 16);
          const g = parseInt(settings.shadow_color.slice(3, 5), 16);
          const b = parseInt(settings.shadow_color.slice(5, 7), 16);
          ctx.shadowColor = `rgba(${r}, ${g}, ${b}, 1)`;
        }
        
        // Convert hex to rgba for background and border
        const bgR = parseInt(settings.background_color.slice(1, 3), 16);
        const bgG = parseInt(settings.background_color.slice(3, 5), 16);
        const bgB = parseInt(settings.background_color.slice(5, 7), 16);
        
        const borderR = parseInt(settings.border_color.slice(1, 3), 16);
        const borderG = parseInt(settings.border_color.slice(3, 5), 16);
        const borderB = parseInt(settings.border_color.slice(5, 7), 16);
        
        // Draw background with rounded corners
        const badgeWidth = img.naturalWidth * (settings.size / 100);
        const badgeHeight = img.naturalHeight * (settings.size / 100);
        
        // Add padding for border
        const paddingX = padding;
        const paddingY = padding;
        
        // Draw rounded rectangle for background
        ctx.beginPath();
        ctx.roundRect(
          centerX - badgeWidth / 2 - paddingX / 2, 
          centerY - badgeHeight / 2 - paddingY / 2,
          badgeWidth + paddingX, 
          badgeHeight + paddingY, 
          settings.border_radius
        );
        ctx.fillStyle = `rgba(${bgR}, ${bgG}, ${bgB}, ${settings.background_transparency})`;
        ctx.fill();
        
        // Draw border if width > 0
        if (settings.border_width > 0) {
          ctx.strokeStyle = `rgba(${borderR}, ${borderG}, ${borderB}, ${settings.border_transparency})`;
          ctx.lineWidth = settings.border_width;
          ctx.stroke();
        }
        
        // Reset shadow before drawing the image
        ctx.shadowColor = 'rgba(0, 0, 0, 0)';
        ctx.shadowBlur = 0;
        ctx.shadowOffsetX = 0;
        ctx.shadowOffsetY = 0;
        
        // Draw the badge image
        ctx.drawImage(
          img,
          centerX - badgeWidth / 2,
          centerY - badgeHeight / 2,
          badgeWidth,
          badgeHeight
        );
        
        // Convert to Base64
        const base64 = canvas.toDataURL('image/png');
        console.log('📷 [imageCaptureUtil] Created base64 image, length:', base64.length);
        resolve(base64);
      } catch (error) {
        console.error('❌ [imageCaptureUtil] Error creating badge image:', error);
        reject(error);
      }
    };
    
    img.onerror = (error) => {
      console.error('❌ [imageCaptureUtil] Error loading badge image:', error, badgeImageSrc);
      reject(new Error('Failed to load badge image'));
    };
    
    // Set crossOrigin after attaching event handlers
    img.crossOrigin = 'anonymous';
    // Set src after setting crossOrigin
    img.src = badgeImageSrc;
  });
};
