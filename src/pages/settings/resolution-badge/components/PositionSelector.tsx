import React from 'react';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';

interface PositionSelectorProps {
  position: string;
  handlePositionChange: (value: string) => void;
}

const PositionSelector: React.FC<PositionSelectorProps> = ({
  position,
  handlePositionChange
}) => {
  return (
    <div className="space-y-3">
      <Label className="text-base">Position</Label>
      <RadioGroup
        value={position}
        onValueChange={handlePositionChange}
        className="grid grid-cols-3 gap-2"
      >
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="top-left" id="top-left" />
          <Label htmlFor="top-left">Top Left</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="top-center" id="top-center" />
          <Label htmlFor="top-center">Top Center</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="top-right" id="top-right" />
          <Label htmlFor="top-right">Top Right</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="bottom-left" id="bottom-left" />
          <Label htmlFor="bottom-left">Bottom Left</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="bottom-center" id="bottom-center" />
          <Label htmlFor="bottom-center">Bottom Center</Label>
        </div>
        <div className="flex items-center space-x-2">
          <RadioGroupItem value="bottom-right" id="bottom-right" />
          <Label htmlFor="bottom-right">Bottom Right</Label>
        </div>
      </RadioGroup>
    </div>
  );
};

export default PositionSelector;
