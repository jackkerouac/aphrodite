import React from 'react';
import { Label } from '@/components/ui/label';
import { Button } from '@/components/ui/button';

interface PositionSelectorProps {
  position: string;
  handlePositionChange: (value: string) => void;
}

const PositionSelector: React.FC<PositionSelectorProps> = ({
  position,
  handlePositionChange
}) => {
  const positions = [
    { value: 'top-left', label: 'Top Left' },
    { value: 'top-center', label: 'Top Center' },
    { value: 'top-right', label: 'Top Right' },
    { value: 'bottom-left', label: 'Bottom Left' },
    { value: 'bottom-center', label: 'Bottom Center' },
    { value: 'bottom-right', label: 'Bottom Right' },
  ];

  return (
    <div className="space-y-2">
      <Label>Position</Label>
      <div className="grid grid-cols-3 gap-2">
        {positions.map((pos) => (
          <Button
            key={pos.value}
            type="button"
            variant={position === pos.value ? 'default' : 'outline'}
            className="h-auto py-2 px-3"
            onClick={() => handlePositionChange(pos.value)}
          >
            {pos.label}
          </Button>
        ))}
      </div>
    </div>
  );
};

export default PositionSelector;