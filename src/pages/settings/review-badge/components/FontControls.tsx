import React from 'react';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { ReviewBadgeSettings } from '../hooks/useReviewBadgeSettings';
import { fontFamilyOptions, scoreFormatOptions } from '../constants';

interface FontControlsProps {
  settings: ReviewBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleSelectChange: (key: string, value: string) => void;
  handleColorChange: (key: string, value: string) => void;
  handleNumberChange: (key: string, value: number) => void;
}

const FontControls: React.FC<FontControlsProps> = ({
  settings,
  handleChange,
  handleSelectChange,
  handleColorChange,
  handleNumberChange
}) => {
  const fontWeightOptions = [
    { value: 400, label: 'Regular (400)' },
    { value: 500, label: 'Medium (500)' },
    { value: 600, label: 'Semibold (600)' },
    { value: 700, label: 'Bold (700)' },
    { value: 800, label: 'Extrabold (800)' }
  ];

  return (
    <div className="space-y-4">
      <div>
        <Label className="text-base">Text Settings</Label>
        <p className="text-xs text-muted-foreground mt-1">
          Customize the appearance of the review score text.
        </p>
      </div>

      {/* Font and Score Format */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="font_family">Font Family</Label>
          <Select 
            value={settings.font_family} 
            onValueChange={(value) => handleSelectChange('font_family', value)}
          >
            <SelectTrigger id="font_family">
              <SelectValue placeholder="Select font" />
            </SelectTrigger>
            <SelectContent>
              {fontFamilyOptions.map((font) => (
                <SelectItem key={font} value={font}>
                  {font}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="score_format">Score Format</Label>
          <Select 
            value={settings.score_format} 
            onValueChange={(value) => handleSelectChange('score_format', value)}
          >
            <SelectTrigger id="score_format">
              <SelectValue placeholder="Select format" />
            </SelectTrigger>
            <SelectContent>
              {scoreFormatOptions.map((format) => (
                <SelectItem key={format} value={format}>
                  {format.charAt(0).toUpperCase() + format.slice(1)}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Font Size and Weight */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="font_size">Font Size (px)</Label>
          <input
            id="font_size"
            type="range"
            name="font_size"
            min="8"
            max="30"
            step="1"
            value={settings.font_size}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs">
            <span>8px</span>
            <span>{settings.font_size}px</span>
            <span>30px</span>
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="font_weight">Font Weight</Label>
          <Select 
            value={settings.font_weight.toString()} 
            onValueChange={(value) => handleNumberChange('font_weight', parseInt(value))}
          >
            <SelectTrigger id="font_weight">
              <SelectValue placeholder="Select weight" />
            </SelectTrigger>
            <SelectContent>
              {fontWeightOptions.map((option) => (
                <SelectItem key={option.value} value={option.value.toString()}>
                  {option.label}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Text Color */}
      <div className="grid grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="text_color">Text Color</Label>
          <div className="flex">
            <Input
              id="text_color"
              type="color"
              value={settings.text_color}
              onChange={(e) => handleColorChange('text_color', e.target.value)}
              className="w-10 h-10 p-1 rounded-l-md"
            />
            <Input
              type="text"
              value={settings.text_color}
              onChange={(e) => handleColorChange('text_color', e.target.value)}
              className="rounded-l-none"
            />
          </div>
        </div>
        <div className="space-y-2">
          <Label htmlFor="text_transparency">Text Transparency</Label>
          <input
            id="text_transparency"
            type="range"
            name="text_transparency"
            min="0"
            max="1"
            step="0.05"
            value={settings.text_transparency}
            onChange={handleChange}
            className="w-full"
          />
          <div className="flex justify-between text-xs">
            <span>0%</span>
            <span>{Math.round(settings.text_transparency * 100)}%</span>
            <span>100%</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default FontControls;
