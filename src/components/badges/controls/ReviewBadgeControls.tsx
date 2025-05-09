import React, { useState, useEffect } from 'react';
import { ReviewBadgeSettings, ReviewSource } from '../types/ReviewBadge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Switch } from '@/components/ui/switch';
import { Button } from '@/components/ui/button';
import { Plus, Trash } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import PositionSelector, { BadgePosition } from '../PositionSelector';

interface ReviewBadgeControlsProps {
  settings: ReviewBadgeSettings;
  onChange: (settings: ReviewBadgeSettings) => void;
}

const ReviewBadgeControls: React.FC<ReviewBadgeControlsProps> = ({ settings, onChange }) => {
  // Local state to track all settings for consistent updates - this is key to making UI controls update properly
  const [localSettings, setLocalSettings] = useState(settings);
  
  // Update local settings when props change
  useEffect(() => {
    setLocalSettings(settings);
  }, [settings]);

  const handleChange = (field: keyof ReviewBadgeSettings, value: any) => {
    // Create new settings based on current local settings
    const newSettings = {
      ...localSettings,
      [field]: value,
    };

    // Update local state first for immediate UI feedback
    setLocalSettings(newSettings);
    
    // Force a synchronous execution to ensure local state is updated
    setTimeout(() => {
      // Then update parent settings
      onChange(newSettings);
    }, 0);
  };

  // Handle position change from the position selector
  const handlePositionChange = (position: BadgePosition) => {
    handleChange('position', position);
  };

  const handleSourceChange = (index: number, field: keyof ReviewSource, value: any) => {
    const updatedSources = [...(localSettings.sources || [])];
    
    if (!updatedSources[index]) {
      updatedSources[index] = { name: '', rating: 0 };
    }
    
    updatedSources[index] = {
      ...updatedSources[index],
      [field]: value,
    };
    
    handleChange('sources', updatedSources);
  };

  const addSource = () => {
    const updatedSources = [...(localSettings.sources || []), { name: '', rating: 0 }];
    handleChange('sources', updatedSources);
  };

  const removeSource = (index: number) => {
    const updatedSources = [...(localSettings.sources || [])];
    updatedSources.splice(index, 1);
    handleChange('sources', updatedSources);
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
                  value={[localSettings.size]} 
                  min={20} 
                  max={200} 
                  step={1}
                  onValueChange={(values) => handleChange('size', values[0])}
                />
                <Input 
                  type="number" 
                  value={localSettings.size} 
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

            {/* Position Selector */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="position">Badge Position</Label>
              <PositionSelector 
                value={localSettings.position as BadgePosition || BadgePosition.BottomLeft} 
                onChange={handlePositionChange}
                className="mt-2"
              />
            </div>

            {/* Padding/Margin Control */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="margin">Edge Padding (px)</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="margin"
                  value={[localSettings.margin || 16]} 
                  min={0} 
                  max={50} 
                  step={1}
                  onValueChange={(values) => handleChange('margin', values[0])}
                />
                <Input 
                  type="number" 
                  value={localSettings.margin || 16} 
                  onChange={(e) => {
                    const newMargin = Math.max(0, Math.min(50, parseFloat(e.target.value) || 0));
                    handleChange('margin', newMargin);
                  }}
                  min={0}
                  max={50}
                  className="w-20"
                />
              </div>
            </div>

            {/* Display Format */}
            <div className="space-y-2 mb-4">
              <Label>Display Format</Label>
              <RadioGroup 
                value={localSettings.displayFormat || 'horizontal'} 
                onValueChange={(value) => handleChange('displayFormat', value)}
                className="flex space-x-4"
              >
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="horizontal" id="horizontal" />
                  <Label htmlFor="horizontal">Horizontal</Label>
                </div>
                <div className="flex items-center space-x-2">
                  <RadioGroupItem value="vertical" id="vertical" />
                  <Label htmlFor="vertical">Vertical</Label>
                </div>
              </RadioGroup>
            </div>

            {/* Max Sources to Show */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="maxSourcesToShow">Max Sources to Show</Label>
              <div className="flex items-center gap-4">
                <Slider 
                  id="maxSourcesToShow"
                  value={[localSettings.maxSourcesToShow || 2]} 
                  min={1} 
                  max={5} 
                  step={1}
                  onValueChange={(values) => handleChange('maxSourcesToShow', values[0])}
                />
                <Input 
                  type="number" 
                  value={localSettings.maxSourcesToShow || 2} 
                  onChange={(e) => handleChange('maxSourcesToShow', parseInt(e.target.value))}
                  className="w-20"
                />
              </div>
            </div>

            {/* Source Dividers */}
            <div className="flex items-center space-x-2 mb-4">
              <Switch
                id="showDividers"
                checked={localSettings.showDividers || false}
                onCheckedChange={(checked) => handleChange('showDividers', checked)}
              />
              <Label htmlFor="showDividers">Show Dividers</Label>
            </div>

            {/* Review Sources */}
            <div className="space-y-2 mt-6">
              <Label className="font-medium">Review Sources</Label>
              <div className="space-y-4 mt-2">
                {(localSettings.sources || []).map((source, index) => (
                  <div key={index} className="flex items-start gap-2 p-3 border rounded-md">
                    <div className="flex-1 space-y-4">
                      <div>
                        <Label htmlFor={`source-${index}-name`} className="text-xs">Source Name</Label>
                        <Input 
                          id={`source-${index}-name`}
                          value={source.name} 
                          onChange={(e) => handleSourceChange(index, 'name', e.target.value)}
                          placeholder="IMDB, Rotten Tomatoes, etc."
                        />
                      </div>
                      <div className="grid grid-cols-2 gap-2">
                        <div>
                          <Label htmlFor={`source-${index}-rating`} className="text-xs">Rating</Label>
                          <Input 
                            id={`source-${index}-rating`}
                            type="number"
                            value={source.rating} 
                            onChange={(e) => handleSourceChange(index, 'rating', parseFloat(e.target.value))}
                            min={0}
                            step={0.1}
                          />
                        </div>
                        <div>
                          <Label htmlFor={`source-${index}-outOf`} className="text-xs">Out Of</Label>
                          <Input 
                            id={`source-${index}-outOf`}
                            type="number"
                            value={source.outOf || 10} 
                            onChange={(e) => handleSourceChange(index, 'outOf', parseFloat(e.target.value))}
                            min={1}
                          />
                        </div>
                      </div>
                    </div>
                    <Button 
                      variant="outline" 
                      size="icon" 
                      onClick={() => removeSource(index)}
                      className="h-8 w-8 mt-3"
                    >
                      <Trash className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button 
                  variant="outline" 
                  onClick={addSource}
                  className="w-full"
                >
                  <Plus className="h-4 w-4 mr-2" /> Add Source
                </Button>
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
                  value={localSettings.backgroundColor} 
                  onChange={(e) => handleChange('backgroundColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input 
                  type="text" 
                  value={localSettings.backgroundColor} 
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
                  value={[localSettings.backgroundOpacity * 100]} 
                  min={0} 
                  max={100} 
                  step={1}
                  onValueChange={(values) => handleChange('backgroundOpacity', values[0] / 100)}
                />
                <span>{Math.round(localSettings.backgroundOpacity * 100)}%</span>
              </div>
            </div>

            {/* Text Color */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="textColor">Text Color</Label>
              <div className="flex gap-2">
                <Input 
                  type="color" 
                  id="textColor"
                  value={localSettings.textColor || '#FFFFFF'} 
                  onChange={(e) => handleChange('textColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input 
                  type="text" 
                  value={localSettings.textColor || '#FFFFFF'} 
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
                  value={[localSettings.fontSize || localSettings.size / 3]} 
                  min={8} 
                  max={72} 
                  step={1}
                  onValueChange={(values) => handleChange('fontSize', values[0])}
                />
                <Input 
                  type="number" 
                  value={localSettings.fontSize || Math.round(localSettings.size / 3)} 
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
                  value={[localSettings.borderRadius || 0]} 
                  min={0} 
                  max={50} 
                  step={1}
                  onValueChange={(values) => handleChange('borderRadius', values[0])}
                />
                <Input 
                  type="number" 
                  value={localSettings.borderRadius || 0} 
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
                  value={[localSettings.borderWidth || 0]} 
                  min={0} 
                  max={10} 
                  step={1}
                  onValueChange={(values) => handleChange('borderWidth', values[0])}
                />
                <Input 
                  type="number" 
                  value={localSettings.borderWidth || 0} 
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
                  value={localSettings.borderColor || '#000000'} 
                  onChange={(e) => handleChange('borderColor', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input 
                  type="text" 
                  value={localSettings.borderColor || '#000000'} 
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
                  value={[(localSettings.borderOpacity || 1) * 100]} 
                  min={0} 
                  max={100} 
                  step={1}
                  onValueChange={(values) => handleChange('borderOpacity', values[0] / 100)}
                />
                <span>{Math.round((localSettings.borderOpacity || 1) * 100)}%</span>
              </div>
            </div>

            {/* Shadow Toggle */}
            <div className="flex items-center space-x-2 mb-4">
              <Switch
                id="shadowEnabled"
                checked={localSettings.shadowEnabled || false}
                onCheckedChange={(checked) => handleChange('shadowEnabled', checked)}
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
                    onChange={(e) => handleChange('shadowColor', e.target.value)}
                    className="w-12 h-8 p-1"
                  />
                  <Input 
                    type="text" 
                    value={localSettings.shadowColor || '#000000'} 
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
                    value={[localSettings.shadowBlur || 5]} 
                    min={0} 
                    max={20} 
                    step={1}
                    onValueChange={(values) => handleChange('shadowBlur', values[0])}
                  />
                  <Input 
                    type="number" 
                    value={localSettings.shadowBlur || 5} 
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
                    value={[localSettings.shadowOffsetX || 2]} 
                    min={-20} 
                    max={20} 
                    step={1}
                    onValueChange={(values) => handleChange('shadowOffsetX', values[0])}
                  />
                  <Input 
                    type="number" 
                    value={localSettings.shadowOffsetX || 2} 
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
                    value={[localSettings.shadowOffsetY || 2]} 
                    min={-20} 
                    max={20} 
                    step={1}
                    onValueChange={(values) => handleChange('shadowOffsetY', values[0])}
                  />
                  <Input 
                    type="number" 
                    value={localSettings.shadowOffsetY || 2} 
                    onChange={(e) => handleChange('shadowOffsetY', parseFloat(e.target.value))}
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

export default ReviewBadgeControls;