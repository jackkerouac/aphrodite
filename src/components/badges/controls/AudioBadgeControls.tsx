import React, { useState } from 'react';
import { AudioBadgeSettings } from '../types/AudioBadge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { audioCodecOptions } from '@/utils/audioCodecUtils';

interface AudioBadgeControlsProps {
  settings: AudioBadgeSettings;
  onChange: (settings: AudioBadgeSettings) => void;
}

const AudioBadgeControls: React.FC<AudioBadgeControlsProps> = ({ settings, onChange }) => {
  // Local state to track all settings for consistent updates
  const [localSettings, setLocalSettings] = useState(settings);
  
  // Update local settings when props change
  React.useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);
  const handleChange = (field: keyof AudioBadgeSettings, value: any) => {
    // Log just the essential info
    console.log(`Updating ${field} to:`, value);
    
    // Create new settings based on current local settings
    const newSettings = {
      ...localSettings,
      [field]: value,
    };

    // When changing size, scale the font size proportionally
    if (field === 'size') {
      // Ensure fontSize is never smaller than 10px for readability
      newSettings.fontSize = Math.max(value / 3, 10);
    }

    // Update local state first for immediate UI feedback
    setLocalSettings(newSettings);
    
    // Force a synchronous execution to ensure local state is updated
    setTimeout(() => {
      // Then update parent settings
      onChange(newSettings);
    }, 0);
  }

  return (
    <div className="space-y-4">
      <Accordion type="single" collapsible className="w-full">
        <AccordionItem value="general">
          <AccordionTrigger>General Settings</AccordionTrigger>
          <AccordionContent>
            {/* Size Control */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="size">Size</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="size-slider"
                  value={[localSettings.size]} 
                  min={20} 
                  max={200} 
                  step={1}
                  onValueChange={(values: number[]) => {
                    const newSize = values[0];
                    handleChange('size', newSize);
                  }}
                />
                <Input 
                  type="number" 
                  value={localSettings.size} 
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => {
                    // Constrain the size to the slider range
                    const newSize = Math.max(20, Math.min(200, parseFloat(e.target.value) || 20));
                    handleChange('size', newSize);
                  }}
                  min={20}
                  max={200}
                  className="w-20"
                />
              </div>
            </div>

            {/* Codec Type Selection */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="codecType">Audio Codec</Label>
              <Select 
                value={localSettings.codecType || 'dolby_atmos'}
                onValueChange={(value: string) => handleChange('codecType', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select codec" />
                </SelectTrigger>
                <SelectContent>
                  {audioCodecOptions.map((option) => (
                    <SelectItem key={option.value} value={option.value}>
                      {option.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <div className="text-xs text-gray-500 mt-1">
                The selected codec will appear as an image in the badge
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="appearance">
          <AccordionTrigger>Appearance</AccordionTrigger>
          <AccordionContent>
            {/* Background Color */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="backgroundColor">Background Color</Label>
              <div className="flex gap-2">
                <Input 
                  type="color" 
                  id="backgroundColor"
                  value={settings.backgroundColor}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('backgroundColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input
                  type="text"
                  value={settings.backgroundColor}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('backgroundColor', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            {/* Background Opacity */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="backgroundOpacity">Background Opacity</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="backgroundOpacity"
                  value={[localSettings.backgroundOpacity * 100]} 
                  min={0} 
                  max={100} 
                  step={1}
                  onValueChange={(values: number[]) => handleChange('backgroundOpacity', values[0] / 100)}
                />
                <span>{Math.round(localSettings.backgroundOpacity * 100)}%</span>
              </div>
            </div>

            {/* Border Size */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="borderWidth">Border Size</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="borderWidth"
                  value={[localSettings.borderWidth || 0]}
                  min={0}
                  max={10}
                  step={1}
                  onValueChange={(values: number[]) => handleChange('borderWidth', values[0])}
                />
                <Input
                  type="number"
                  value={localSettings.borderWidth || 0}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('borderWidth', parseFloat(e.target.value))}
                  className="w-20"
                />
              </div>
            </div>

            {/* Border Color */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="borderColor">Border Color</Label>
              <div className="flex gap-2">
                <Input
                  type="color"
                  id="borderColor"
                  value={localSettings.borderColor || '#000000'}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('borderColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input
                  type="text"
                  value={localSettings.borderColor || '#000000'}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('borderColor', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            {/* Border Opacity */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="borderOpacity">Border Opacity</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="borderOpacity"
                  value={[localSettings.borderOpacity === undefined ? 100 : localSettings.borderOpacity * 100]}
                  min={0}
                  max={100}
                  step={1}
                  onValueChange={(values: number[]) => handleChange('borderOpacity', values[0] / 100)}
                />
                <span>{Math.round((localSettings.borderOpacity === undefined ? 100 : localSettings.borderOpacity * 100))}%</span>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        <AccordionItem value="border">
          <AccordionTrigger>Border & Shadow</AccordionTrigger>
          <AccordionContent>
            {/* Border Radius */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="borderRadius">Border Radius</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="borderRadius"
                  value={[localSettings.borderRadius || 0]} 
                  min={0} 
                  max={50} 
                  step={1}
                  onValueChange={(values: number[]) => handleChange('borderRadius', values[0])}
                />
                <Input 
                  type="number" 
                  value={localSettings.borderRadius || 0}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('borderRadius', parseFloat(e.target.value))}
                  className="w-20"
                />
              </div>
            </div>

            {/* Border Width */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="borderWidthSettings">Border Width</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="borderWidthSettings"
                  value={[localSettings.borderWidth || 0]} 
                  min={0} 
                  max={10} 
                  step={1}
                  onValueChange={(values: number[]) => handleChange('borderWidth', values[0])}
                />
                <Input 
                  type="number" 
                  value={localSettings.borderWidth || 0}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('borderWidth', parseFloat(e.target.value))}
                  className="w-20"
                />
              </div>
            </div>

            {/* Shadow Toggle */}
            <div className="flex items-center space-x-2 mb-4">
              <Switch
                id="shadowEnabled"
                checked={localSettings.shadowEnabled || false}
                onCheckedChange={(checked: boolean) => handleChange('shadowEnabled', checked)}
              />
              <Label htmlFor="shadowEnabled">Enable Shadow</Label>
            </div>

            {/* Shadow Settings - Use a fixed height container with conditional rendering */}
            <div className={`shadow-settings-container ${!localSettings.shadowEnabled ? 'hidden' : 'block'} space-y-4`}>
              {/* Shadow Color */}
              <div className="space-y-2 mb-4">
                <Label htmlFor="shadowColor">Shadow Color</Label>
                <div className="flex gap-2">
                  <Input 
                    type="color" 
                    id="shadowColor"
                    value={localSettings.shadowColor || '#000000'}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('shadowColor', e.target.value)}
                    className="w-12 h-8 p-1"
                  />
                  <Input
                    type="text"
                    value={localSettings.shadowColor || '#000000'}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('shadowColor', e.target.value)}
                    className="flex-1"
                  />
                </div>
              </div>

              {/* Shadow Blur */}
              <div className="space-y-2 mb-4">
                <Label htmlFor="shadowBlur">Shadow Blur</Label>
                <div className="flex items-center gap-4">
                  <Slider 
                    id="shadowBlur"
                    value={[localSettings.shadowBlur || 5]} 
                    min={0} 
                    max={20} 
                    step={1}
                    onValueChange={(values: number[]) => handleChange('shadowBlur', values[0])}
                  />
                  <Input 
                    type="number" 
                    value={localSettings.shadowBlur || 5}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('shadowBlur', parseFloat(e.target.value))}
                    className="w-20"
                  />
                </div>
              </div>

              {/* Shadow Offset X */}
              <div className="space-y-2 mb-4">
                <Label htmlFor="shadowOffsetX">Shadow Offset X</Label>
                <div className="flex items-center gap-4">
                  <Slider 
                    id="shadowOffsetX"
                    value={[localSettings.shadowOffsetX || 2]} 
                    min={-20} 
                    max={20} 
                    step={1}
                    onValueChange={(values: number[]) => handleChange('shadowOffsetX', values[0])}
                  />
                  <Input 
                    type="number" 
                    value={localSettings.shadowOffsetX || 2}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('shadowOffsetX', parseFloat(e.target.value))}
                    className="w-20"
                  />
                </div>
              </div>

              {/* Shadow Offset Y */}
              <div className="space-y-2 mb-4">
                <Label htmlFor="shadowOffsetY">Shadow Offset Y</Label>
                <div className="flex items-center gap-4">
                  <Slider 
                    id="shadowOffsetY"
                    value={[localSettings.shadowOffsetY || 2]} 
                    min={-20} 
                    max={20} 
                    step={1}
                    onValueChange={(values: number[]) => handleChange('shadowOffsetY', values[0])}
                  />
                  <Input 
                    type="number" 
                    value={localSettings.shadowOffsetY || 2}
                    onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('shadowOffsetY', parseFloat(e.target.value))}
                    className="w-20"
                  />
                </div>
              </div>
            </div>

            {/* Add a placeholder div with specific height when shadow settings are hidden */}
            {!localSettings.shadowEnabled && (
              <div className="shadow-placeholder h-0 overflow-hidden opacity-0"></div>
            )}
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
};

export default AudioBadgeControls;