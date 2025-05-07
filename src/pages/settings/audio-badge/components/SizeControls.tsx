import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { AudioBadgeSettings } from '../hooks/useAudioBadgeSettings';

interface SizeControlsProps {
  settings: AudioBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
}

const SizeControls: React.FC<SizeControlsProps> = ({
  settings,
  handleChange
}) => {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <div className="flex justify-between">
          <Label htmlFor="size">Size ({settings.size}%)</Label>
          <span className="text-xs text-muted-foreground">Percentage of original size</span>
        </div>
        <div className="flex items-center space-x-2">
          <Slider
            id="size"
            min={50}
            max={150}
            step={5}
            value={[settings.size]}
            onValueChange={(values) => {
              const event = {
                target: {
                  name: 'size',
                  value: values[0].toString()
                }
              } as React.ChangeEvent<HTMLInputElement>;
              handleChange(event);
            }}
          />
          <Input
            type="number"
            id="size-input"
            name="size"
            className="w-16"
            value={settings.size}
            onChange={handleChange}
            min={50}
            max={150}
            step={5}
          />
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between">
          <Label htmlFor="margin">Margin ({settings.margin}px)</Label>
          <span className="text-xs text-muted-foreground">Distance from poster edge</span>
        </div>
        <div className="flex items-center space-x-2">
          <Slider
            id="margin"
            min={0}
            max={50}
            step={1}
            value={[settings.margin]}
            onValueChange={(values) => {
              const event = {
                target: {
                  name: 'margin',
                  value: values[0].toString()
                }
              } as React.ChangeEvent<HTMLInputElement>;
              handleChange(event);
            }}
          />
          <Input
            type="number"
            id="margin-input"
            name="margin"
            className="w-16"
            value={settings.margin}
            onChange={handleChange}
            min={0}
            max={50}
            step={1}
          />
        </div>
      </div>

      <div className="space-y-2">
        <div className="flex justify-between">
          <Label htmlFor="z_index">Z-Index ({settings.z_index})</Label>
          <span className="text-xs text-muted-foreground">Layer position</span>
        </div>
        <div className="flex items-center space-x-2">
          <Slider
            id="z_index"
            min={0}
            max={10}
            step={1}
            value={[settings.z_index]}
            onValueChange={(values) => {
              const event = {
                target: {
                  name: 'z_index',
                  value: values[0].toString()
                }
              } as React.ChangeEvent<HTMLInputElement>;
              handleChange(event);
            }}
          />
          <Input
            type="number"
            id="z_index-input"
            name="z_index"
            className="w-16"
            value={settings.z_index}
            onChange={handleChange}
            min={0}
            max={10}
            step={1}
          />
        </div>
      </div>
    </div>
  );
};

export default SizeControls;