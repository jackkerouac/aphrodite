import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { AudioBadgeSettings } from '../hooks/useAudioBadgeSettings';

interface ShadowControlsProps {
  settings: AudioBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleColorChange: (key: string, value: string) => void;
  handleToggleChange: (key: string, value: boolean) => void;
}

const ShadowControls: React.FC<ShadowControlsProps> = ({
  settings,
  handleChange,
  handleColorChange,
  handleToggleChange
}) => {
  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Label htmlFor="shadow-toggle" className="text-lg font-semibold">Shadow</Label>
        <Switch
          id="shadow-toggle"
          checked={settings.shadow_toggle}
          onCheckedChange={(checked) => handleToggleChange('shadow_toggle', checked)}
        />
      </div>
      
      {settings.shadow_toggle && (
        <div className="space-y-4 pl-2 border-l-2 border-muted p-2">
          <div className="flex items-center space-x-2">
            <Input
              type="color"
              id="shadow_color"
              name="shadow_color"
              className="w-14 h-8 p-1"
              value={settings.shadow_color}
              onChange={(e) => handleColorChange('shadow_color', e.target.value)}
            />
            <div className="flex-1">
              <Label htmlFor="shadow_color">Shadow Color</Label>
            </div>
          </div>

          <div>
            <Label htmlFor="shadow_blur_radius">Blur Radius</Label>
            <div className="flex items-center space-x-2 mt-1">
              <Slider
                id="shadow_blur_radius"
                min={0}
                max={20}
                step={1}
                value={[settings.shadow_blur_radius]}
                onValueChange={(values) => {
                  const event = {
                    target: {
                      name: 'shadow_blur_radius',
                      value: values[0].toString()
                    }
                  } as React.ChangeEvent<HTMLInputElement>;
                  handleChange(event);
                }}
              />
              <Input
                type="number"
                id="shadow_blur_radius-input"
                name="shadow_blur_radius"
                className="w-16"
                value={settings.shadow_blur_radius}
                onChange={handleChange}
                min={0}
                max={20}
                step={1}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="shadow_offset_x">X Offset</Label>
              <div className="flex items-center space-x-2 mt-1">
                <Slider
                  id="shadow_offset_x"
                  min={-20}
                  max={20}
                  step={1}
                  value={[settings.shadow_offset_x]}
                  onValueChange={(values) => {
                    const event = {
                      target: {
                        name: 'shadow_offset_x',
                        value: values[0].toString()
                      }
                    } as React.ChangeEvent<HTMLInputElement>;
                    handleChange(event);
                  }}
                />
                <Input
                  type="number"
                  id="shadow_offset_x-input"
                  name="shadow_offset_x"
                  className="w-16"
                  value={settings.shadow_offset_x}
                  onChange={handleChange}
                  min={-20}
                  max={20}
                  step={1}
                />
              </div>
            </div>
            <div>
              <Label htmlFor="shadow_offset_y">Y Offset</Label>
              <div className="flex items-center space-x-2 mt-1">
                <Slider
                  id="shadow_offset_y"
                  min={-20}
                  max={20}
                  step={1}
                  value={[settings.shadow_offset_y]}
                  onValueChange={(values) => {
                    const event = {
                      target: {
                        name: 'shadow_offset_y',
                        value: values[0].toString()
                      }
                    } as React.ChangeEvent<HTMLInputElement>;
                    handleChange(event);
                  }}
                />
                <Input
                  type="number"
                  id="shadow_offset_y-input"
                  name="shadow_offset_y"
                  className="w-16"
                  value={settings.shadow_offset_y}
                  onChange={handleChange}
                  min={-20}
                  max={20}
                  step={1}
                />
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShadowControls;