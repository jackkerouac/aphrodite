import React from 'react';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ReviewBadgeSettings } from '../hooks/useReviewBadgeSettings';

interface LogoControlsProps {
  settings: ReviewBadgeSettings;
  handleToggleChange: (key: string, value: boolean) => void;
  handleNumberChange: (key: string, value: number) => void;
  handleSelectChange: (key: string, value: string) => void;
}

const LogoControls: React.FC<LogoControlsProps> = ({
  settings,
  handleToggleChange,
  handleNumberChange,
  handleSelectChange
}) => {
  return (
    <div className="space-y-4">
      <div>
        <Label className="text-base">Logo Settings</Label>
        <p className="text-xs text-muted-foreground mt-1">
          Configure how rating source logos should be displayed.
        </p>
      </div>

      {/* Show Logo Toggle */}
      <div className="flex items-center justify-between">
        <Label htmlFor="show_logo" className="cursor-pointer">
          Show Rating Source Logo
        </Label>
        <Switch
          id="show_logo"
          checked={settings.show_logo}
          onCheckedChange={(checked) => handleToggleChange('show_logo', checked)}
        />
      </div>

      {/* Logo Size and Position - only shown when logo is enabled */}
      {settings.show_logo && (
        <>
          <div className="space-y-2">
            <Label htmlFor="logo_size">Logo Size (px)</Label>
            <input
              id="logo_size"
              type="range"
              min="16"
              max="128"
              step="1"
              value={settings.logo_size}
              onChange={(e) => handleNumberChange('logo_size', parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs">
              <span>16px</span>
              <span>{settings.logo_size}px</span>
              <span>128px</span>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="logo_text_spacing">Logo-Text Spacing (px)</Label>
            <input
              id="logo_text_spacing"
              type="range"
              min="0"
              max="20"
              step="1"
              value={settings.logoTextSpacing}
              onChange={(e) => handleNumberChange('logoTextSpacing', parseInt(e.target.value))}
              className="w-full"
            />
            <div className="flex justify-between text-xs">
              <span>0px</span>
              <span>{settings.logoTextSpacing}px</span>
              <span>20px</span>
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="logo_position">Logo Position</Label>
            <Select 
              value={settings.logo_position} 
              onValueChange={(value) => handleSelectChange('logo_position', value)}
            >
              <SelectTrigger id="logo_position">
                <SelectValue placeholder="Select position" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="top">Above Score</SelectItem>
                <SelectItem value="bottom">Below Score</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </>
      )}
    </div>
  );
};

export default LogoControls;
