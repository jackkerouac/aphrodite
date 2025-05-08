import { BadgeRenderingCommonOptions } from '../badgeRenderer';

/**
 * Helper function to create a temporary canvas in the DOM
 * @param width Width of the canvas
 * @param height Height of the canvas
 * @returns HTMLCanvasElement
 */
export const createTempCanvas = (width: number, height: number): HTMLCanvasElement => {
  const canvas = document.createElement('canvas');
  canvas.width = width;
  canvas.height = height;
  return canvas;
};

/**
 * Helper function to draw a rounded rectangle
 * @param ctx Canvas context
 * @param x X position
 * @param y Y position
 * @param width Width of the rectangle
 * @param height Height of the rectangle
 * @param radius Corner radius (can be capped by the function)
 */
export const drawRoundedRect = (
  ctx: CanvasRenderingContext2D,
  x: number,
  y: number,
  width: number,
  height: number,
  radius: number
) => {
  // Cap the radius at half the smaller dimension to prevent distortion
  const maxRadius = Math.min(width / 2, height / 2);
  const r = Math.min(radius, maxRadius);
  
  // If radius is effectively zero, draw a normal rectangle
  if (r < 1) {
    ctx.rect(x, y, width, height);
    return;
  }
  
  // Draw rounded rectangle path
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.lineTo(x + width - r, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + r);
  ctx.lineTo(x + width, y + height - r);
  ctx.quadraticCurveTo(x + width, y + height, x + width - r, y + height);
  ctx.lineTo(x + r, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - r);
  ctx.lineTo(x, y + r);
  ctx.quadraticCurveTo(x, y, x + r, y);
  ctx.closePath();
};

/**
 * Extracts a badge from a canvas with transparent background
 * @param canvas The canvas containing the badge
 * @param badgeBounds The bounds of the badge to extract
 * @returns Base64 encoded PNG data URL
 */
export const extractBadgeWithTransparency = (
  canvas: HTMLCanvasElement,
  badgeBounds: {x: number, y: number, width: number, height: number}
): string => {
  const tempCanvas = document.createElement('canvas');
  tempCanvas.width = badgeBounds.width;
  tempCanvas.height = badgeBounds.height;
  const tempCtx = tempCanvas.getContext('2d');

  if (!tempCtx) {
    throw new Error("Could not get canvas context");
  }

  tempCtx.clearRect(0, 0, tempCanvas.width, tempCanvas.height);
  tempCtx.drawImage(
    canvas,
    badgeBounds.x,
    badgeBounds.y,
    badgeBounds.width,
    badgeBounds.height,
    0,
    0,
    badgeBounds.width,
    badgeBounds.height
  );

  return tempCanvas.toDataURL('image/png');
};