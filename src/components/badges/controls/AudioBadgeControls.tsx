import React from 'react';
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
  const handleChange = (field: keyof AudioBadgeSettings, value: any) => {
    let newSettings: AudioBadgeSettings = {
      ...settings,
      [field]: value,
    };

    if (field === 'size') {
      newSettings.fontSize = value / 3;
    }

    onChange(newSettings);
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
                  id="size"
                  value={[settings.size]} 
                  min={20} 
                  max={200} 
                  step={1}
                  onValueChange={(values: number[]) => handleChange('size', values[0])}
                />
                <Input 
                  type="number" 
                  value={settings.size} 
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
                value={settings.codecType || 'dolby_atmos'}
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
                  value={[settings.backgroundOpacity * 100]} 
                  min={0} 
                  max={100} 
                  step={1}
                  onValueChange={(values: number[]) => handleChange('backgroundOpacity', values[0] / 100)}
                />
                <span>{Math.round(settings.backgroundOpacity * 100)}%</span>
              </div>
            </div>

            {/* Border Size */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="borderWidth">Border Size</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="borderWidth"
                  value={[settings.borderWidth || 0]}
                  min={0}
                  max={10}
                  step={1}
                  onValueChange={(values: number[]) => handleChange('borderWidth', values[0])}
                />
                <Input
                  type="number"
                  value={settings.borderWidth || 0}
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
                  value={settings.borderColor || '#000000'}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('borderColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input
                  type="text"
                  value={settings.borderColor || '#000000'}
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
                  value={[settings.borderOpacity === undefined ? 100 : settings.borderOpacity * 100]}
                  min={0}
                  max={100}
                  step={1}
                  onValueChange={(values: number[]) => handleChange('borderOpacity', values[0] / 100)}
                />
                <span>{Math.round((settings.borderOpacity === undefined ? 100 : settings.borderOpacity * 100))}%</span>
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
                  value={[settings.borderRadius || 0]} 
                  min={0} 
                  max={50} 
                  step={1}
                  onValueChange={(values: number[]) => handleChange('borderRadius', values[0])}
                />
                <Input 
                  type="number" 
                  value={settings.borderRadius || 0}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('borderRadius', parseFloat(e.target.value))}
                  className="w-20"
                />
              </div>
            </div>

            {/* Border Width */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="borderWidth">Border Width</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="borderWidth"
                  value={[settings.borderWidth || 0]} 
                  min={0} 
                  max={10} 
                  step={1}
                  onValueChange={(values: number[]) => handleChange('borderWidth', values[0])}
                />
                <Input 
                  type="number" 
                  value={settings.borderWidth || 0}
                  onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('borderWidth', parseFloat(e.target.value))}
                  className="w-20"
                />
              </div>
            </div>

            {/* Shadow Toggle */}
            <div className="flex items-center space-x-2 mb-4">
              <Switch
                id="shadowEnabled"
                checked={settings.shadowEnabled || false}
                onCheckedChange={(checked: boolean) => handleChange('shadowEnabled', checked)}
              />
              <Label htmlFor="shadowEnabled">Enable Shadow</Label>
            </div>

            {settings.shadowEnabled && (
              <>
                {/* Shadow Color */}
                <div className="space-y-2 mb-4">
                  <Label htmlFor="shadowColor">Shadow Color</Label>
                  <div className="flex gap-2">
                    <Input 
                      type="color" 
                      id="shadowColor"
                      value={settings.shadowColor || '#000000'}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('shadowColor', e.target.value)}
                      className="w-12 h-8 p-1"
                    />
                    <Input
                      type="text"
                      value={settings.shadowColor || '#000000'}
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
                      value={[settings.shadowBlur || 5]} 
                      min={0} 
                      max={20} 
                      step={1}
                      onValueChange={(values: number[]) => handleChange('shadowBlur', values[0])}
                    />
                    <Input 
                      type="number" 
                      value={settings.shadowBlur || 5}
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
                      value={[settings.shadowOffsetX || 2]} 
                      min={-20} 
                      max={20} 
                      step={1}
                      onValueChange={(values: number[]) => handleChange('shadowOffsetX', values[0])}
                    />
                    <Input 
                      type="number" 
                      value={settings.shadowOffsetX || 2}
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
                      value={[settings.shadowOffsetY || 2]} 
                      min={-20} 
                      max={20} 
                      step={1}
                      onValueChange={(values: number[]) => handleChange('shadowOffsetY', values[0])}
                    />
                    <Input 
                      type="number" 
                      value={settings.shadowOffsetY || 2}
                      onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange('shadowOffsetY', parseFloat(e.target.value))}
                      className="w-20"
                    />
                  </div>
                </div>
              </>
            )}
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
};

export default AudioBadgeControls;