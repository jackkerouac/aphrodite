import html2canvas from 'html2canvas';

/**
 * Captures a DOM element as a Base64 image
 * @param elementRef - React ref to the DOM element to capture
 * @returns Promise resolving to the Base64 image data
 */
export const captureBadgeAsBase64 = async (elementRef: React.RefObject<HTMLDivElement>): Promise<string | null> => {
  if (!elementRef.current) {
    console.error('Element reference is not available');
    return null;
  }

  try {
    const element = elementRef.current;

    // Make sure element is rendered and has dimensions
    if (element.offsetWidth === 0 || element.offsetHeight === 0) {
      console.error('Element has zero width or height, cannot capture image');
      return null;
    }

    console.log('[captureBadgeAsBase64] Element details:', {
      width: element.offsetWidth,
      height: element.offsetHeight,
      hasChildren: element.childNodes.length > 0,
      position: window.getComputedStyle(element).position,
      visibility: window.getComputedStyle(element).visibility,
      display: window.getComputedStyle(element).display
    });

    // Capture the element using html2canvas
    const canvas = await html2canvas(element, {
      backgroundColor: null, // Transparent background
      scale: 2, // Higher resolution
      logging: true, // Enable logging for debugging
      useCORS: true, // Allow cross-origin images
      allowTaint: true // Allow tainted canvas
    });

    // Convert to Base64
    const imageData = canvas.toDataURL('image/png');
    return imageData;
  } catch (error) {
    console.error('Failed to capture badge as image:', error);
    return null;
  }
};