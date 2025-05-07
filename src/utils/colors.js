/**
 * Utility functions for working with colors in the Aphrodite UI
 */

/**
 * Get the appropriate color for a status
 * @param {string} status - The status ('success', 'warning', 'error', or any other value)
 * @returns {string} The CSS variable for the status color
 */
export const getStatusColor = (status) => {
  const statusMap = {
    success: 'var(--success)',
    warning: 'var(--warning)',
    error: 'var(--error)',
    default: 'var(--neutral)'
  };
  
  return statusMap[status] || statusMap.default;
};

/**
 * Convert a hex color and transparency to rgba format
 * @param {string} hexColor - Hex color code (e.g., "#4C1D95")
 * @param {number} transparency - Value between 0 and 1
 * @returns {string} RGBA color string
 */
export const hexToRgba = (hexColor, transparency = 1) => {
  // Remove # if present
  const hex = hexColor.replace('#', '');
  
  // Parse the hex values
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  
  // Return rgba value
  return `rgba(${r}, ${g}, ${b}, ${transparency})`;
};

/**
 * Get the appropriate color for light/dark mode context
 * @param {string} lightColor - Color to use in light mode
 * @param {string} darkColor - Color to use in dark mode
 * @param {boolean} isDarkMode - Whether dark mode is active
 * @returns {string} The appropriate color based on the mode
 */
export const getThemeColor = (lightColor, darkColor, isDarkMode) => {
  return isDarkMode ? darkColor : lightColor;
};
