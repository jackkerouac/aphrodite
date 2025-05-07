import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { ReviewBadgeSettings } from '../hooks/useReviewBadgeSettings';

interface ShadowControlsProps {
  settings: ReviewBadgeSettings;
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
        <Label htmlFor="shadow_toggle" className="cursor-pointer">
          Enable Shadow
        </Label>
        <Switch
          id="shadow_toggle"
          checked={settings.shadow_toggle}
          onCheckedChange={(checked) => handleToggleChange('shadow_toggle', checked)}
        />
      </div>

      {settings.shadow_toggle && (
        <>
          {/* Shadow Color */}
          <div className="space-y-2">
            <Label htmlFor="shadow_color">Shadow Color</Label>
            <div className="flex">
              <Input
                id="shadow_color"
                type="color"
                value={settings.shadow_color}
                onChange={(e) => handleColorChange('shadow_color', e.target.value)}
                className="w-10 h-10 p-1 rounded-l-md"
              />
              <Input
                type="text"
                value={settings.shadow_color}
                onChange={(e) => handleColorChange('shadow_color', e.target.value)}
                className="rounded-l-none"
              />
            </div>
          </div>

          {/* Shadow Blur Radius */}
          <div className="space-y-2">
            <Label htmlFor="shadow_blur_radius">Shadow Blur Radius (px)</Label>
            <input
              id="shadow_blur_radius"
              type="range"
              name="shadow_blur_radius"
              min="0"
              max="20"
              step="1"
              value={settings.shadow_blur_radius}
              onChange={handleChange}
              className="w-full"
            />
            <div className="flex justify-between text-xs">
              <span>0px</span>
              <span>{settings.shadow_blur_radius}px</span>
              <span>20px</span>
            </div>
          </div>

          {/* Shadow Offset X */}
          <div className="space-y-2">
            <Label htmlFor="shadow_offset_x">Shadow Offset X (px)</Label>
            <input
              id="shadow_offset_x"
              type="range"
              name="shadow_offset_x"
              min="-20"
              max="20"
              step="1"
              value={settings.shadow_offset_x}
              onChange={handleChange}
              className="w-full"
            />
            <div className="flex justify-between text-xs">
              <span>-20px</span>
              <span>{settings.shadow_offset_x}px</span>
              <span>20px</span>
            </div>
          </div>

          {/* Shadow Offset Y */}
          <div className="space-y-2">
            <Label htmlFor="shadow_offset_y">Shadow Offset Y (px)</Label>
            <input
              id="shadow_offset_y"
              type="range"
              name="shadow_offset_y"
              min="-20"
              max="20"
              step="1"
              value={settings.shadow_offset_y}
              onChange={handleChange}
              className="w-full"
            />
            <div className="flex justify-between text-xs">
              <span>-20px</span>
              <span>{settings.shadow_offset_y}px</span>
              <span>20px</span>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ShadowControls;
