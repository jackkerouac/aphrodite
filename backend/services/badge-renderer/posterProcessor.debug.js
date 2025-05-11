// This is a test snippet to add debug logging to the badge positioning
// Add this to the calculateSafePosition method in posterProcessor.js

calculateSafePosition(position, posterWidth, posterHeight, badgeWidth, badgeHeight, margin) {
  let left = 0;
  let top = 0;
  
  // Enhanced debug logging
  console.log('calculateSafePosition called with:', {
    position,
    posterWidth,
    posterHeight,
    badgeWidth,
    badgeHeight,
    margin,
    marginType: typeof margin
  });
  
  switch (position) {
    case 'top-left':
      left = margin;
      top = margin;
      break;
    case 'top-right':
      left = posterWidth - badgeWidth - margin;
      top = margin;
      break;
    case 'bottom-left':
      left = margin;
      top = posterHeight - badgeHeight - margin;
      break;
    case 'bottom-right':
      left = posterWidth - badgeWidth - margin;
      top = posterHeight - badgeHeight - margin;
      break;
    default:
      // Default to bottom-right
      left = posterWidth - badgeWidth - margin;
      top = posterHeight - badgeHeight - margin;
  }
  
  // Ensure position is within bounds
  const originalLeft = left;
  const originalTop = top;
  left = Math.max(0, Math.min(left, posterWidth - badgeWidth));
  top = Math.max(0, Math.min(top, posterHeight - badgeHeight));
  
  if (originalLeft !== left || originalTop !== top) {
    console.log('Position was clamped:', {
      originalLeft,
      originalTop,
      clampedLeft: left,
      clampedTop: top
    });
  }
  
  console.log(`Badge position for ${position}:`, {
    left,
    top,
    margin,
    centerX: left + badgeWidth/2,
    centerY: top + badgeHeight/2,
    distanceFromLeftEdge: left,
    distanceFromTopEdge: top,
    distanceFromRightEdge: posterWidth - (left + badgeWidth),
    distanceFromBottomEdge: posterHeight - (top + badgeHeight)
  });
  
  return { left, top };
}

// Also add more logging to applyBadgesWithCanvas
console.log('Badge settings transformation:', {
  originalSettings: config.settings,
  originalMargin: config.settings.margin,
  originalPadding: config.settings.padding,
  scaleFactor,
  marginScaleFactor: cappedMarginScaleFactor,
  scaledMargin: scaledSettings.margin,
  scaledPadding: scaledSettings.padding
});
