import { BadgePosition, BADGE_POSITION_PADDING } from '@/components/badges/PositionSelector';

// Type for calculated CSS positioning properties
export interface BadgePositionStyles {
  top?: string;
  right?: string;
  bottom?: string;
  left?: string;
  transform?: string;
}

/**
 * Converts a BadgePosition enum value to appropriate CSS positioning properties
 * @param position The BadgePosition enum value
 * @param padding The padding in pixels from the edge (defaults to BADGE_POSITION_PADDING)
 * @returns CSS style object with appropriate positioning properties
 */
export const getBadgePositionStyles = (
  position: BadgePosition,
  padding: number = BADGE_POSITION_PADDING
): BadgePositionStyles => {
  const paddingPx = `${padding}px`;
  
  switch (position) {
    case BadgePosition.TopLeft:
      return { top: paddingPx, left: paddingPx };
    
    case BadgePosition.TopCenter:
      return { 
        top: paddingPx, 
        left: '50%', 
        transform: 'translateX(-50%)' 
      };
    
    case BadgePosition.TopRight:
      return { top: paddingPx, right: paddingPx };
    
    case BadgePosition.MiddleLeft:
      return { 
        top: '50%', 
        left: paddingPx, 
        transform: 'translateY(-50%)' 
      };
    
    case BadgePosition.Center:
      return { 
        top: '50%', 
        left: '50%', 
        transform: 'translate(-50%, -50%)' 
      };
    
    case BadgePosition.MiddleRight:
      return { 
        top: '50%', 
        right: paddingPx, 
        transform: 'translateY(-50%)' 
      };
    
    case BadgePosition.BottomLeft:
      return { bottom: paddingPx, left: paddingPx };
    
    case BadgePosition.BottomCenter:
      return { 
        bottom: paddingPx, 
        left: '50%', 
        transform: 'translateX(-50%)' 
      };
    
    case BadgePosition.BottomRight:
      return { bottom: paddingPx, right: paddingPx };
    
    default:
      // Default to top-left if an invalid position is provided
      return { top: paddingPx, left: paddingPx };
  }
};

/**
 * Converts a legacy position string (e.g., 'top-right') to the new BadgePosition enum
 * @param legacyPosition The old position string or object with percentX/percentY
 * @returns The corresponding BadgePosition enum value
 */
export const convertLegacyPosition = (
  legacyPosition: string | { percentX: number; percentY: number }
): BadgePosition => {
  // If we have a percentX/percentY object, convert based on quadrants
  if (typeof legacyPosition === 'object' && 'percentX' in legacyPosition && 'percentY' in legacyPosition) {
    const { percentX, percentY } = legacyPosition;
    
    // Determine horizontal position (left, center, right)
    let horizontal: 'left' | 'center' | 'right';
    if (percentX < 33) {
      horizontal = 'left';
    } else if (percentX > 66) {
      horizontal = 'right';
    } else {
      horizontal = 'center';
    }
    
    // Determine vertical position (top, middle, bottom)
    let vertical: 'top' | 'middle' | 'bottom';
    if (percentY < 33) {
      vertical = 'top';
    } else if (percentY > 66) {
      vertical = 'bottom';
    } else {
      vertical = 'middle';
    }
    
    // Special case for center
    if (vertical === 'middle' && horizontal === 'center') {
      return BadgePosition.Center;
    }
    
    // Combine to get the position
    return BadgePosition[`${vertical}${horizontal.charAt(0).toUpperCase() + horizontal.slice(1)}` as keyof typeof BadgePosition];
  }
  
  // Handle legacy string positions
  if (typeof legacyPosition === 'string') {
    // Parse positions like 'top-left', 'bottom-right', etc.
    if (legacyPosition === 'top-left') return BadgePosition.TopLeft;
    if (legacyPosition === 'top-center') return BadgePosition.TopCenter;
    if (legacyPosition === 'top-right') return BadgePosition.TopRight;
    if (legacyPosition === 'middle-left') return BadgePosition.MiddleLeft;
    if (legacyPosition === 'center') return BadgePosition.Center;
    if (legacyPosition === 'middle-right') return BadgePosition.MiddleRight;
    if (legacyPosition === 'bottom-left') return BadgePosition.BottomLeft;
    if (legacyPosition === 'bottom-center') return BadgePosition.BottomCenter;
    if (legacyPosition === 'bottom-right') return BadgePosition.BottomRight;
  }
  
  // Default to top-left if we can't determine
  return BadgePosition.TopLeft;
};
