import React from 'react';
import { Label } from '@/components/ui/label';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { layoutOptions } from '../constants';

interface LayoutSelectorProps {
  layout: string;
  handleSelectChange: (value: string) => void;
}

const LayoutSelector: React.FC<LayoutSelectorProps> = ({
  layout,
  handleSelectChange
}) => {
  return (
    <div className="space-y-3">
      <Label className="text-base">Badge Layout</Label>
      <RadioGroup
        value={layout}
        onValueChange={handleSelectChange}
        className="flex flex-col space-y-2"
      >
        <div className="flex gap-6">
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="horizontal" id="horizontal" />
            <Label htmlFor="horizontal" className="cursor-pointer flex gap-2 items-center">
              <span>Horizontal</span>
              <div className="w-12 h-6 border rounded-md flex items-center px-1">
                <div className="w-4 h-4 bg-primary rounded-sm"></div>
                <div className="ml-1 w-5 h-4 bg-muted rounded-sm"></div>
              </div>
            </Label>
          </div>
          
          <div className="flex items-center space-x-2">
            <RadioGroupItem value="vertical" id="vertical" />
            <Label htmlFor="vertical" className="cursor-pointer flex gap-2 items-center">
              <span>Vertical</span>
              <div className="w-6 h-12 border rounded-md flex flex-col items-center py-1">
                <div className="w-4 h-4 bg-primary rounded-sm"></div>
                <div className="mt-1 w-4 h-5 bg-muted rounded-sm"></div>
              </div>
            </Label>
          </div>
        </div>
      </RadioGroup>
    </div>
  );
};

export default LayoutSelector;
