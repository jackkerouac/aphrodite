import React from 'react';
import { ResolutionBadgeSettings } from '../types/ResolutionBadge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { resolutionOptions } from '@/pages/settings/resolution-badge/constants';
import { getResolutionDisplayName } from '@/utils/resolutionUtils';

interface ResolutionBadgeControlsProps {
  settings: ResolutionBadgeSettings;
  onChange: (settings: ResolutionBadgeSettings) => void;
}

const ResolutionBadgeControls: React.FC<ResolutionBadgeControlsProps> = ({ settings, onChange }) => {
  const handleSliderChange = (field: keyof ResolutionBadgeSettings, value: number) => {
    // Immediately update the slider value and preview
    onChange({
      ...settings,
      [field]: value,
    });
  };
  
  const handleColorSliderChange = (field: keyof ResolutionBadgeSettings, value: number) => {
    // For opacity sliders, convert the percentage to a decimal value
    onChange({
      ...settings,
      [field]: value / 100,
    });
  };

  const handleChange = (field: keyof ResolutionBadgeSettings, value: any) => {
    onChange({
      ...settings,
      [field]: value,
    });
  };

  // Helper function to sort resolutions in a logical order
  const getSortedResolutions = () => {
    // Define resolution categories for sorting
    const categories = {
      standard: ['4k', '2160', '1080', '1080p', '720', '720p', '576p', '480', '480p'],
      plus: ['4kplus', '1080pplus', '720pplus', '576pplus', '480pplus', 'plus'],
      hdr: ['4khdr', '1080phdr', '720phdr', '576phdr', '480phdr', 'hdr'],
      dv: ['4kdv', '1080pdv', '720pdv', '576pdv', '480pdv', 'dv'],
      advanced: ['4kdvhdr', '4kdvhdrplus', '1080pdvhdr', '1080pdvhdrplus', '720pdvhdr', '720pdvhdrplus', 
               '576pdvhdr', '576pdvhdrplus', '480pdvhdr', '480pdvhdrplus', 'dvhdr', 'dvhdrplus']
    };
    
    // Create a lookup map for sorting within categories
    const resolutionOrder: Record<string, number> = {};
    
    // Assign sort values to each resolution type
    let sortIndex = 0;
    
    // First add standard resolutions in descending order
    categories.standard.forEach(res => {
      resolutionOrder[res] = sortIndex++;
    });
    
    // Then add plus versions
    categories.plus.forEach(res => {
      resolutionOrder[res] = sortIndex++;
    });
    
    // Then add HDR versions
    categories.hdr.forEach(res => {
      resolutionOrder[res] = sortIndex++;
    });
    
    // Then add DV versions
    categories.dv.forEach(res => {
      resolutionOrder[res] = sortIndex++;
    });
    
    // Finally add advanced combinations
    categories.advanced.forEach(res => {
      resolutionOrder[res] = sortIndex++;
    });
    
    // Sort the resolutions
    return [...resolutionOptions].sort((a, b) => {
      // If both resolutions are in our order map, use that
      if (resolutionOrder[a] !== undefined && resolutionOrder[b] !== undefined) {
        return resolutionOrder[a] - resolutionOrder[b];
      }
      
      // Otherwise, just sort alphabetically
      return a.localeCompare(b);
    });
  };
  
  // Get the sorted resolutions
  const sortedResolutions = getSortedResolutions();

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
                  onValueChange={(values) => handleSliderChange('size', values[0])}
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
                value={settings.resolutionType || '4k'}
                onValueChange={(value) => handleChange('resolutionType', value)}
              >
                <SelectTrigger>
                  <SelectValue placeholder="Select resolution" />
                </SelectTrigger>
                <SelectContent>
                  {sortedResolutions.map((resolution) => (
                    <SelectItem key={resolution} value={resolution}>
                      {getResolutionDisplayName(resolution)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            {/* Removed "Use Custom Text" toggle as requested */}
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
                  onValueChange={(values) => handleColorSliderChange('backgroundOpacity', values[0])}
                />
                <span>{Math.round(settings.backgroundOpacity * 100)}%</span>
              </div>
            </div>
            
            {/* Removed Text Color and Font Size functionality as requested */}
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
                  onValueChange={(values) => handleSliderChange('borderRadius', values[0])}
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
                  onValueChange={(values) => handleSliderChange('borderWidth', values[0])}
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

            {/* Border Opacity */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="borderOpacity">Border Opacity</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="borderOpacity"
                  value={[(settings.borderOpacity || 1) * 100]} 
                  min={0} 
                  max={100} 
                  step={1}
                  onValueChange={(values) => handleColorSliderChange('borderOpacity', values[0])}
                />
                <span>{Math.round((settings.borderOpacity || 1) * 100)}%</span>
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
                      onValueChange={(values) => handleSliderChange('shadowBlur', values[0])}
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
                      onValueChange={(values) => handleSliderChange('shadowOffsetX', values[0])}
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
                      onValueChange={(values) => handleSliderChange('shadowOffsetY', values[0])}
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