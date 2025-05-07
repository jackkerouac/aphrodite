import React from 'react';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { ResolutionBadgeSettings } from '../hooks/useResolutionBadgeSettings';
import ColorPicker from '../../ColorPicker';

interface ShadowControlsProps {
  settings: ResolutionBadgeSettings;
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
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <Label htmlFor="shadow_toggle" className="text-base">Enable Shadow</Label>
        <Switch
          id="shadow_toggle"
          checked={settings.shadow_toggle}
          onCheckedChange={(checked) => handleToggleChange('shadow_toggle', checked)}
        />
      </div>

      {settings.shadow_toggle && (
        <div className="space-y-4 mt-4">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <Label htmlFor="shadow_color" className="mb-2 block">Shadow Color</Label>
              <ColorPicker
                color={settings.shadow_color}
                onChange={(color) => handleColorChange('shadow_color', color)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="shadow_blur_radius">Blur ({settings.shadow_blur_radius}px)</Label>
              <Slider
                id="shadow_blur_radius"
                name="shadow_blur_radius"
                min={0}
                max={20}
                step={1}
                value={[settings.shadow_blur_radius]}
                onValueChange={handleSliderChange('shadow_blur_radius')}
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="shadow_offset_x">Offset X ({settings.shadow_offset_x}px)</Label>
              <Slider
                id="shadow_offset_x"
                name="shadow_offset_x"
                min={-20}
                max={20}
                step={1}
                value={[settings.shadow_offset_x]}
                onValueChange={handleSliderChange('shadow_offset_x')}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="shadow_offset_y">Offset Y ({settings.shadow_offset_y}px)</Label>
              <Slider
                id="shadow_offset_y"
                name="shadow_offset_y"
                min={-20}
                max={20}
                step={1}
                value={[settings.shadow_offset_y]}
                onValueChange={handleSliderChange('shadow_offset_y')}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ShadowControls;
