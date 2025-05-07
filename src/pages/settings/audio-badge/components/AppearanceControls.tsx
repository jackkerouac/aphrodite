import React from 'react';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { AudioBadgeSettings } from '../hooks/useAudioBadgeSettings';

// Import the ColorPicker component
import ColorPicker from '../../ColorPicker';

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
      {/* Background Settings */}
      <div className="space-y-3">
        <Label className="text-base">Background</Label>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="background_color" className="mb-2 block">Color</Label>
            <ColorPicker
              color={settings.background_color}
              onChange={(color) => handleColorChange('background_color', color)}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="background_transparency">
              Transparency ({(settings.background_transparency * 100).toFixed(0)}%)
            </Label>
            <Slider
              id="background_transparency"
              name="background_transparency"
              min={0}
              max={1}
              step={0.01}
              value={[settings.background_transparency]}
              onValueChange={handleSliderChange('background_transparency')}
            />
          </div>
        </div>
      </div>

      {/* Border Settings */}
      <div className="space-y-3">
        <Label className="text-base">Border</Label>
        
        <div className="grid grid-cols-2 gap-4">
          <div>
            <Label htmlFor="border_color" className="mb-2 block">Color</Label>
            <ColorPicker
              color={settings.border_color}
              onChange={(color) => handleColorChange('border_color', color)}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="border_transparency">
              Transparency ({(settings.border_transparency * 100).toFixed(0)}%)
            </Label>
            <Slider
              id="border_transparency"
              name="border_transparency"
              min={0}
              max={1}
              step={0.01}
              value={[settings.border_transparency]}
              onValueChange={handleSliderChange('border_transparency')}
            />
          </div>
        </div>
        
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="border_width">Width ({settings.border_width}px)</Label>
            <Slider
              id="border_width"
              name="border_width"
              min={0}
              max={10}
              step={1}
              value={[settings.border_width]}
              onValueChange={handleSliderChange('border_width')}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="border_radius">Radius ({settings.border_radius}px)</Label>
            <Slider
              id="border_radius"
              name="border_radius"
              min={0}
              max={20}
              step={1}
              value={[settings.border_radius]}
              onValueChange={handleSliderChange('border_radius')}
            />
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppearanceControls;