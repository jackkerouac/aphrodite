import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";

/**
 * Utility function to merge Tailwind CSS classes with clsx
 * 
 * Combines clsx and tailwind-merge to handle class conflicts appropriately
 * 
 * @param  {...any} inputs - CSS class values to be merged
 * @returns {string} Merged CSS classes
 */
export function cn(...inputs) {
  return twMerge(clsx(inputs));
}

/**
 * Format a value with a specific unit
 * 
 * @param {number|string} value - The value to format
 * @param {string} unit - The unit to append (px, %, etc.)
 * @returns {string} Formatted value with unit
 */
export function formatWithUnit(value, unit = "px") {
  if (typeof value === "number") {
    return `${value}${unit}`;
  }
  
  if (typeof value === "string" && !isNaN(parseFloat(value))) {
    return value.includes(unit) ? value : `${value}${unit}`;
  }
  
  return value;
}

/**
 * Convert a hex color value to RGBA
 * 
 * @param {string} hex - Hex color code (e.g., #4C1D95)
 * @param {number} alpha - Alpha transparency value (0-1)
 * @returns {string} RGBA color value
 */
export function hexToRgba(hex, alpha = 1) {
  // Remove # if present
  const cleanHex = hex.replace("#", "");
  
  // Parse the hex values
  const r = parseInt(cleanHex.substring(0, 2), 16);
  const g = parseInt(cleanHex.substring(2, 4), 16);
  const b = parseInt(cleanHex.substring(4, 6), 16);
  
  // Return rgba value
  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

/**
 * Generate a unique ID with a prefix
 * 
 * @param {string} prefix - Prefix for the ID
 * @returns {string} Unique ID
 */
export function generateId(prefix = "aphrodite") {
  return `${prefix}-${Math.random().toString(36).substring(2, 9)}`;
}

/**
 * Wait for a specified duration
 * 
 * @param {number} ms - Time to wait in milliseconds
 * @returns {Promise} Promise that resolves after the specified time
 */
export function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
