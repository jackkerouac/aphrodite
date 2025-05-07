import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { AudioBadgeSettings } from '../hooks/useAudioBadgeSettings';

interface AppearanceControlsProps {
  settings: AudioBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleColorChange: (key: string, value: string) => void;
}

const AppearanceControls: React.FC<AppearanceControlsProps> = ({
  settings,
  handleChange,
  handleColorChange
}) => {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold">Appearance</h2>
      
      {/* Background settings */}
      <div className="space-y-2">
        <Label>Background</Label>
        <div className="flex items-center space-x-2">
          <Input
            type="color"
            id="background_color"
            name="background_color"
            className="w-14 h-8 p-1"
            value={settings.background_color}
            onChange={(e) => handleColorChange('background_color', e.target.value)}
          />
          <div className="flex-1">
            <div className="flex justify-between mb-2">
              <Label htmlFor="background_transparency">Transparency ({Math.round(settings.background_transparency * 100)}%)</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Slider
                id="background_transparency"
                min={0}
                max={1}
                step={0.01}
                value={[settings.background_transparency]}
                onValueChange={(values) => {
                  const event = {
                    target: {
                      name: 'background_transparency',
                      value: values[0].toString()
                    }
                  } as React.ChangeEvent<HTMLInputElement>;
                  handleChange(event);
                }}
              />
            </div>
          </div>
        </div>
      </div>

      {/* Border settings */}
      <div className="space-y-2">
        <Label>Border</Label>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="border_radius">Border Radius</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Slider
                id="border_radius"
                min={0}
                max={20}
                step={1}
                value={[settings.border_radius]}
                onValueChange={(values) => {
                  const event = {
                    target: {
                      name: 'border_radius',
                      value: values[0].toString()
                    }
                  } as React.ChangeEvent<HTMLInputElement>;
                  handleChange(event);
                }}
              />
              <Input
                type="number"
                id="border_radius-input"
                name="border_radius"
                className="w-16"
                value={settings.border_radius}
                onChange={handleChange}
                min={0}
                max={20}
                step={1}
              />
            </div>
          </div>
          <div>
            <Label htmlFor="border_width">Border Width</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Slider
                id="border_width"
                min={0}
                max={10}
                step={1}
                value={[settings.border_width]}
                onValueChange={(values) => {
                  const event = {
                    target: {
                      name: 'border_width',
                      value: values[0].toString()
                    }
                  } as React.ChangeEvent<HTMLInputElement>;
                  handleChange(event);
                }}
              />
              <Input
                type="number"
                id="border_width-input"
                name="border_width"
                className="w-16"
                value={settings.border_width}
                onChange={handleChange}
                min={0}
                max={10}
                step={1}
              />
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-2 mt-2">
          <Input
            type="color"
            id="border_color"
            name="border_color"
            className="w-14 h-8 p-1"
            value={settings.border_color}
            onChange={(e) => handleColorChange('border_color', e.target.value)}
          />
          <div className="flex-1">
            <div className="flex justify-between mb-2">
              <Label htmlFor="border_transparency">Border Transparency ({Math.round(settings.border_transparency * 100)}%)</Label>
            </div>
            <div className="flex items-center space-x-2">
              <Slider
                id="border_transparency"
                min={0}
                max={1}
                step={0.01}
                value={[settings.border_transparency]}
                onValueChange={(values) => {
                  const event = {
                    target: {
                      name: 'border_transparency',
                      value: values[0].toString()
                    }
                  } as React.ChangeEvent<HTMLInputElement>;
                  handleChange(event);
                }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppearanceControls;