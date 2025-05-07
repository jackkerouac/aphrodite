import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { ReviewBadgeSettings } from '../hooks/useReviewBadgeSettings';

interface AppearanceControlsProps {
  settings: ReviewBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleColorChange: (key: string, value: string) => void;
}

const AppearanceControls: React.FC<AppearanceControlsProps> = ({
  settings,
  handleChange,
  handleColorChange
}) => {
  return (
    <div className="space-y-4">
      <div>
        <Label className="text-base">Background & Border</Label>
        <p className="text-xs text-muted-foreground mt-1">
          Customize the appearance of the badge background and border.
        </p>
      </div>

      {/* Background Color */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="background_color">Background Color</Label>
          <div className="flex">
            <Input
              id="background_color"
              type="color"
              value={settings.background_color}
              onChange={(e) => handleColorChange('background_color', e.target.value)}
              className="w-10 h-10 p-1 rounded-l-md"
            />
            <Input
              type="text"
              value={settings.background_color}
              onChange={(e) => handleColorChange('background_color', e.target.value)}
              className="rounded-l-none"
            />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="background_transparency">Background Transparency</Label>
          <input
            id="background_transparency"
            type="range"
            name="background_transparency"
            min="0"
            max="1"
            step="0.05"
            value={settings.background_transparency}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs">
            <span>0%</span>
            <span>{Math.round(settings.background_transparency * 100)}%</span>
            <span>100%</span>
          </div>
        </div>
      </div>

      {/* Border Settings */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="border_radius">Border Radius (px)</Label>
          <input
            id="border_radius"
            type="range"
            name="border_radius"
            min="0"
            max="20"
            step="1"
            value={settings.border_radius}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs">
            <span>0px</span>
            <span>{settings.border_radius}px</span>
            <span>20px</span>
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="border_width">Border Width (px)</Label>
          <input
            id="border_width"
            type="range"
            name="border_width"
            min="0"
            max="10"
            step="1"
            value={settings.border_width}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs">
            <span>0px</span>
            <span>{settings.border_width}px</span>
            <span>10px</span>
          </div>
        </div>
      </div>

      {/* Border Color */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="border_color">Border Color</Label>
          <div className="flex">
            <Input
              id="border_color"
              type="color"
              value={settings.border_color}
              onChange={(e) => handleColorChange('border_color', e.target.value)}
              className="w-10 h-10 p-1 rounded-l-md"
            />
            <Input
              type="text"
              value={settings.border_color}
              onChange={(e) => handleColorChange('border_color', e.target.value)}
              className="rounded-l-none"
            />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="border_transparency">Border Transparency</Label>
          <input
            id="border_transparency"
            type="range"
            name="border_transparency"
            min="0"
            max="1"
            step="0.05"
            value={settings.border_transparency}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs">
            <span>0%</span>
            <span>{Math.round(settings.border_transparency * 100)}%</span>
            <span>100%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AppearanceControls;
