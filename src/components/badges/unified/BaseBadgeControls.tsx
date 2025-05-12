import React from 'react';
import { BaseBadgeSettings, BadgePosition } from '@/types/unifiedBadgeSettings';
import { Label } from '@/components/ui/label';
import { Slider } from '@/components/ui/slider';
import { Input } from '@/components/ui/input';
import { Switch } from '@/components/ui/switch';
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from '@/components/ui/accordion';
import PositionSelector from '@/components/badges/PositionSelector';

interface BaseBadgeControlsProps<T extends BaseBadgeSettings> {
  settings: T;
  onChange: (settings: T) => void;
  badgeType: string;
}

/**
 * Base component for all badge controls with common settings
 */
export function BaseBadgeControls<T extends BaseBadgeSettings>({
  settings,
  onChange,
  badgeType,
  children
}: React.PropsWithChildren<BaseBadgeControlsProps<T>>) {
  // Update a specific field in the settings
  const handleChange = (field: keyof BaseBadgeSettings, value: any) => {
    onChange({
      ...settings,
      [field]: value,
    } as T);
  };

  // Handle position change from the position selector
  const handlePositionChange = (position: BadgePosition) => {
    handleChange('badge_position', position);
  };

  return (
    <div className="space-y-4">
      <Accordion type="single" collapsible defaultValue="general" className="w-full">
        {/* General Settings Section */}
        <AccordionItem value="general">
          <AccordionTrigger>General Settings</AccordionTrigger>
          <AccordionContent>
            {/* Badge Type Display */}
            <div className="mb-4 pb-2 border-b border-gray-200">
              <Label className="text-sm font-medium">Badge Type</Label>
              <div className="text-sm mt-1 capitalize">{badgeType}</div>
            </div>

            {/* Badge Size */}
            <div className="space-y-2 mb-4">
              <div className="flex items-center justify-between">
                <Label htmlFor="badge_size">Badge Size</Label>
                <div className="text-xs text-muted-foreground">
                  {badgeType === 'review' ? 'Absolute Size' : 'Scale %'}
                </div>
              </div>
              <div className="flex items-center gap-4">
                <Slider
                  id="badge_size"
                  value={[settings.badge_size]}
                  min={20}
                  max={500}
                  step={1}
                  onValueChange={(values) => handleChange('badge_size', values[0])}
                />
                <Input
                  type="number"
                  value={settings.badge_size}
                  onChange={(e) => {
                    const newSize = Math.max(20, Math.min(500, parseInt(e.target.value) || 20));
                    handleChange('badge_size', newSize);
                  }}
                  min={20}
                  max={500}
                  className="w-20"
                />
              </div>
              {badgeType !== 'review' && (
                <p className="text-xs text-muted-foreground mt-1">
                  For {badgeType} badges, this value represents a scaling factor where 100 = original size.
                </p>
              )}
            </div>

            {/* Edge Padding */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="edge_padding">Edge Padding (px)</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="edge_padding"
                  value={[settings.edge_padding]}
                  min={0}
                  max={50}
                  step={1}
                  onValueChange={(values) => handleChange('edge_padding', values[0])}
                />
                <Input
                  type="number"
                  value={settings.edge_padding}
                  onChange={(e) => {
                    const newPadding = Math.max(0, Math.min(50, parseInt(e.target.value) || 0));
                    handleChange('edge_padding', newPadding);
                  }}
                  min={0}
                  max={50}
                  className="w-20"
                />
              </div>
            </div>

            {/* Badge Position */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="badge_position">Badge Position</Label>
              <PositionSelector
                value={settings.badge_position}
                onChange={handlePositionChange}
                className="mt-2"
              />
            </div>

            {/* Badge-specific controls */}
            {children}
          </AccordionContent>
        </AccordionItem>

        {/* Background Settings Section */}
        <AccordionItem value="background">
          <AccordionTrigger>Background</AccordionTrigger>
          <AccordionContent>
            {/* Background Color */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="background_color">Background Color</Label>
              <div className="flex gap-2">
                <Input
                  type="color"
                  id="background_color"
                  value={settings.background_color}
                  onChange={(e) => handleChange('background_color', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input
                  type="text"
                  value={settings.background_color}
                  onChange={(e) => handleChange('background_color', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            {/* Background Opacity */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="background_opacity">Background Opacity</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="background_opacity"
                  value={[settings.background_opacity]}
                  min={0}
                  max={100}
                  step={1}
                  onValueChange={(values) => handleChange('background_opacity', values[0])}
                />
                <span>{settings.background_opacity}%</span>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Border Settings Section */}
        <AccordionItem value="border">
          <AccordionTrigger>Border</AccordionTrigger>
          <AccordionContent>
            {/* Border Size */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="border_size">Border Size</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="border_size"
                  value={[settings.border_size]}
                  min={0}
                  max={10}
                  step={1}
                  onValueChange={(values) => handleChange('border_size', values[0])}
                />
                <Input
                  type="number"
                  value={settings.border_size}
                  onChange={(e) => {
                    const newSize = Math.max(0, Math.min(10, parseInt(e.target.value) || 0));
                    handleChange('border_size', newSize);
                  }}
                  min={0}
                  max={10}
                  className="w-20"
                />
              </div>
            </div>

            {/* Border Color */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="border_color">Border Color</Label>
              <div className="flex gap-2">
                <Input
                  type="color"
                  id="border_color"
                  value={settings.border_color}
                  onChange={(e) => handleChange('border_color', e.target.value)}
                  className="w-12 h-8 p-1"
                />
                <Input
                  type="text"
                  value={settings.border_color}
                  onChange={(e) => handleChange('border_color', e.target.value)}
                  className="flex-1"
                />
              </div>
            </div>

            {/* Border Opacity */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="border_opacity">Border Opacity</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="border_opacity"
                  value={[settings.border_opacity]}
                  min={0}
                  max={100}
                  step={1}
                  onValueChange={(values) => handleChange('border_opacity', values[0])}
                />
                <span>{settings.border_opacity}%</span>
              </div>
            </div>

            {/* Border Radius */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="border_radius">Border Radius</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="border_radius"
                  value={[settings.border_radius]}
                  min={0}
                  max={50}
                  step={1}
                  onValueChange={(values) => handleChange('border_radius', values[0])}
                />
                <Input
                  type="number"
                  value={settings.border_radius}
                  onChange={(e) => {
                    const newRadius = Math.max(0, Math.min(50, parseInt(e.target.value) || 0));
                    handleChange('border_radius', newRadius);
                  }}
                  min={0}
                  max={50}
                  className="w-20"
                />
              </div>
            </div>

            {/* Border Width */}
            <div className="space-y-2 mb-4">
              <Label htmlFor="border_width">Border Width</Label>
              <div className="flex items-center gap-4">
                <Slider
                  id="border_width"
                  value={[settings.border_width]}
                  min={0}
                  max={10}
                  step={1}
                  onValueChange={(values) => handleChange('border_width', values[0])}
                />
                <Input
                  type="number"
                  value={settings.border_width}
                  onChange={(e) => {
                    const newWidth = Math.max(0, Math.min(10, parseInt(e.target.value) || 0));
                    handleChange('border_width', newWidth);
                  }}
                  min={0}
                  max={10}
                  className="w-20"
                />
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>

        {/* Shadow Settings Section */}
        <AccordionItem value="shadow">
          <AccordionTrigger>Shadow</AccordionTrigger>
          <AccordionContent>
            {/* Shadow Toggle */}
            <div className="flex items-center space-x-2 mb-4">
              <Switch
                id="shadow_enabled"
                checked={settings.shadow_enabled}
                onCheckedChange={(checked) => handleChange('shadow_enabled', checked)}
              />
              <Label htmlFor="shadow_enabled">Enable Shadow</Label>
            </div>

            {/* Shadow Settings - Only shown when shadow is enabled */}
            <div className={`${settings.shadow_enabled ? 'block' : 'hidden'} space-y-4`}>
              {/* Shadow Color */}
              <div className="space-y-2 mb-4">
                <Label htmlFor="shadow_color">Shadow Color</Label>
                <div className="flex gap-2">
                  <Input
                    type="color"
                    id="shadow_color"
                    value={settings.shadow_color}
                    onChange={(e) => handleChange('shadow_color', e.target.value)}
                    className="w-12 h-8 p-1"
                  />
                  <Input
                    type="text"
                    value={settings.shadow_color}
                    onChange={(e) => handleChange('shadow_color', e.target.value)}
                    className="flex-1"
                  />
                </div>
              </div>

              {/* Shadow Blur */}
              <div className="space-y-2 mb-4">
                <Label htmlFor="shadow_blur">Shadow Blur</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    id="shadow_blur"
                    value={[settings.shadow_blur]}
                    min={0}
                    max={20}
                    step={1}
                    onValueChange={(values) => handleChange('shadow_blur', values[0])}
                  />
                  <Input
                    type="number"
                    value={settings.shadow_blur}
                    onChange={(e) => {
                      const newBlur = Math.max(0, Math.min(20, parseInt(e.target.value) || 0));
                      handleChange('shadow_blur', newBlur);
                    }}
                    min={0}
                    max={20}
                    className="w-20"
                  />
                </div>
              </div>

              {/* Shadow Offset X */}
              <div className="space-y-2 mb-4">
                <Label htmlFor="shadow_offset_x">Shadow Offset X</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    id="shadow_offset_x"
                    value={[settings.shadow_offset_x]}
                    min={-20}
                    max={20}
                    step={1}
                    onValueChange={(values) => handleChange('shadow_offset_x', values[0])}
                  />
                  <Input
                    type="number"
                    value={settings.shadow_offset_x}
                    onChange={(e) => {
                      const newOffsetX = Math.max(-20, Math.min(20, parseInt(e.target.value) || 0));
                      handleChange('shadow_offset_x', newOffsetX);
                    }}
                    min={-20}
                    max={20}
                    className="w-20"
                  />
                </div>
              </div>

              {/* Shadow Offset Y */}
              <div className="space-y-2 mb-4">
                <Label htmlFor="shadow_offset_y">Shadow Offset Y</Label>
                <div className="flex items-center gap-4">
                  <Slider
                    id="shadow_offset_y"
                    value={[settings.shadow_offset_y]}
                    min={-20}
                    max={20}
                    step={1}
                    onValueChange={(values) => handleChange('shadow_offset_y', values[0])}
                  />
                  <Input
                    type="number"
                    value={settings.shadow_offset_y}
                    onChange={(e) => {
                      const newOffsetY = Math.max(-20, Math.min(20, parseInt(e.target.value) || 0));
                      handleChange('shadow_offset_y', newOffsetY);
                    }}
                    min={-20}
                    max={20}
                    className="w-20"
                  />
                </div>
              </div>
            </div>
          </AccordionContent>
        </AccordionItem>
      </Accordion>
    </div>
  );
}

export default BaseBadgeControls;
