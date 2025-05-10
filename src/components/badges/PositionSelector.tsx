import React from 'react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

export enum BadgePosition {
  TopLeft = 'top-left',
  TopCenter = 'top-center',
  TopRight = 'top-right',
  MiddleLeft = 'middle-left',
  Center = 'center',
  MiddleRight = 'middle-right',
  BottomLeft = 'bottom-left',
  BottomCenter = 'bottom-center',
  BottomRight = 'bottom-right',
}

export const BADGE_POSITION_PADDING = 16; // Default padding in pixels from the edge

interface PositionSelectorProps {
  value: BadgePosition;
  onChange: (position: BadgePosition) => void;
  className?: string;
}

const PositionSelector: React.FC<PositionSelectorProps> = ({
  value,
  onChange,
  className,
}) => {
  const positionGrid = [
    [BadgePosition.TopLeft, BadgePosition.TopCenter, BadgePosition.TopRight],
    [BadgePosition.MiddleLeft, BadgePosition.Center, BadgePosition.MiddleRight],
    [BadgePosition.BottomLeft, BadgePosition.BottomCenter, BadgePosition.BottomRight],
  ];

  // Helper to get a nice display name for the position
  const getPositionDisplayName = (position: BadgePosition): string => {
    return position
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  return (
    <div className={cn("grid grid-cols-3 gap-2 w-full", className)}>
      {positionGrid.map((row, rowIndex) => (
        <React.Fragment key={`position-row-${rowIndex}`}>
          {row.map((position) => (
            <Button
              key={position}
              type="button"
              variant={value === position ? "default" : "outline"}
              onClick={() => onChange(position)}
              className="h-9 text-xs p-1 flex items-center justify-center"
              title={getPositionDisplayName(position)}
            >
              {getPositionDisplayName(position)}
            </Button>
          ))}
        </React.Fragment>
      ))}
    </div>
  );
};

export default PositionSelector;
