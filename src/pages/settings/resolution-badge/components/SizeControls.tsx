import React from 'react';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { ResolutionBadgeSettings } from '../hooks/useResolutionBadgeSettings';

interface SizeControlsProps {
  settings: ResolutionBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const SizeControls: React.FC<SizeControlsProps> = ({ settings, handleChange }) => {
  // Custom handler for slider that creates the expected event object
  const handleSliderChange = (name: string) => (value: number[]) => {
    const syntheticEvent = {
      target: {
        name,
        value: value[0].toString(),
      },
    } as React.ChangeEvent<HTMLInputElement>;
    
    handleChange(syntheticEvent);
  };

  return (
    <div className="space-y-4">
      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <Label htmlFor="size">Size ({settings.size}%)</Label>
        </div>
        <Slider
          id="size"
          name="size"
          min={10}
          max={200}
          step={1}
          value={[settings.size]}
          onValueChange={handleSliderChange('size')}
        />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <Label htmlFor="margin">Margin ({settings.margin}px)</Label>
        </div>
        <Slider
          id="margin"
          name="margin"
          min={0}
          max={50}
          step={1}
          value={[settings.margin]}
          onValueChange={handleSliderChange('margin')}
        />
      </div>

      <div className="space-y-2">
        <div className="flex justify-between items-center">
          <Label htmlFor="z_index">Z-Index ({settings.z_index})</Label>
        </div>
        <Slider
          id="z_index"
          name="z_index"
          min={1}
          max={10}
          step={1}
          value={[settings.z_index]}
          onValueChange={handleSliderChange('z_index')}
        />
      </div>
    </div>
  );
};

export default SizeControls;
