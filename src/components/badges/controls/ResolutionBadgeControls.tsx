import React from 'react';
import { ResolutionBadgeSettings } from '../types/ResolutionBadge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';

interface ResolutionBadgeControlsProps {
  settings: ResolutionBadgeSettings;
  onChange: (settings: ResolutionBadgeSettings) => void;
}

const ResolutionBadgeControls: React.FC<ResolutionBadgeControlsProps> = ({ settings, onChange }) => {
  const handleChange = (field: keyof ResolutionBadgeSettings, value: any) => {
    onChange({
      ...settings,
      [field]: value,
    });
  };

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
                  onValueChange={(values) => handleChange('size', values[0])}
                />
                <Input 
                  type="number" 
                  value={settings.size} 
                  onChange={(e) => {
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

            {/* Resolution Type Selection */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="resolutionType">Resolution</Label>
              <Select 
                value={settings.resolutionType || '4K'}
                onValueChange={(value) => handleChange('resolutionType', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select resolution" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="4K">4K</SelectItem>
                  <SelectItem value="1080p">1080p</SelectItem>
                  <SelectItem value="720p">720p</SelectItem>
                  <SelectItem value="8K">8K</SelectItem>
                  <SelectItem value="SD">SD</SelectItem>
                  <SelectItem value="HDR">HDR</SelectItem>
                  <SelectItem value="Dolby Vision">Dolby Vision</SelectItem>
                </SelectContent>
              </Select>
            </div>

            {/* Custom Text Toggle */}
            <div className="flex items-center space-x-2 mb-4">
              <Switch
                id="useCustomText"
                checked={settings.useCustomText || false}
                onCheckedChange={(checked) => handleChange('useCustomText', checked)}
              />
              <Label htmlFor="useCustomText">Use Custom Text</Label>
            </div>

            {/* Custom Text Input */}
            {settings.useCustomText && (
              <div className="space-y-2 mb-4">
                <Label htmlFor="customText">Custom Text</Label>
                <Input 
                  id="customText"
                  value={settings.customText || ''} 
                  onChange={(e) => handleChange('customText', e.target.value)}
                />
              </div>
            )}
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
                  onChange={(e) => handleChange('backgroundColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input 
                  type="text" 
                  value={settings.backgroundColor} 
                  onChange={(e) => handleChange('backgroundColor', e.target.value)}
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
                  onValueChange={(values) => handleChange('backgroundOpacity', values[0] / 100)}
                />
                <span>{Math.round(settings.backgroundOpacity * 100)}%</span>
              </div>
            </div>

            {/* Text Color */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="textColor">Text Color</Label>
              <div className="flex gap-2">
                <Input 
                  type="color" 
                  id="textColor"
                  value={settings.textColor || '#FFFFFF'} 
                  onChange={(e) => handleChange('textColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input 
                  type="text" 
                  value={settings.textColor || '#FFFFFF'} 
                  onChange={(e) => handleChange('textColor', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            {/* Font Size */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="fontSize">Font Size</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="fontSize"
                  value={[settings.fontSize || settings.size / 2]} 
                  min={8} 
                  max={72} 
                  step={1}
                  onValueChange={(values) => handleChange('fontSize', values[0])}
                />
                <Input 
                  type="number" 
                  value={settings.fontSize || Math.round(settings.size / 2)} 
                  onChange={(e) => handleChange('fontSize', parseFloat(e.target.value))}
                  className="w-20"
                />
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
                  onValueChange={(values) => handleChange('borderRadius', values[0])}
                />
                <Input 
                  type="number" 
                  value={settings.borderRadius || 0} 
                  onChange={(e) => handleChange('borderRadius', parseFloat(e.target.value))}
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
                  onValueChange={(values) => handleChange('borderWidth', values[0])}
                />
                <Input 
                  type="number" 
                  value={settings.borderWidth || 0} 
                  onChange={(e) => handleChange('borderWidth', parseFloat(e.target.value))}
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
                  onChange={(e) => handleChange('borderColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input 
                  type="text" 
                  value={settings.borderColor || '#000000'} 
                  onChange={(e) => handleChange('borderColor', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            {/* Shadow Toggle */}
            <div className="flex items-center space-x-2 mb-4">
              <Switch
                id="shadowEnabled"
                checked={settings.shadowEnabled || false}
                onCheckedChange={(checked) => handleChange('shadowEnabled', checked)}
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
                      onChange={(e) => handleChange('shadowColor', e.target.value)}
                      className="w-12 h-8 p-1"
                    />
                    <Input 
                      type="text" 
                      value={settings.shadowColor || '#000000'} 
                      onChange={(e) => handleChange('shadowColor', e.target.value)}
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
                      onValueChange={(values) => handleChange('shadowBlur', values[0])}
                    />
                    <Input 
                      type="number" 
                      value={settings.shadowBlur || 5} 
                      onChange={(e) => handleChange('shadowBlur', parseFloat(e.target.value))}
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
                      onValueChange={(values) => handleChange('shadowOffsetX', values[0])}
                    />
                    <Input 
                      type="number" 
                      value={settings.shadowOffsetX || 2} 
                      onChange={(e) => handleChange('shadowOffsetX', parseFloat(e.target.value))}
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
                      onValueChange={(values) => handleChange('shadowOffsetY', values[0])}
                    />
                    <Input 
                      type="number" 
                      value={settings.shadowOffsetY || 2} 
                      onChange={(e) => handleChange('shadowOffsetY', parseFloat(e.target.value))}
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

export default ResolutionBadgeControls;