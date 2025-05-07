import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { H2, BodyLarge, Body, Label } from '../ui/typography';
import { Select } from '../ui/select';
import { Slider } from '../ui/slider';
import { Input } from '../ui/input';
import { Button } from '../ui/button';
import { PositionGrid } from '../ui/position-grid';
import { ColorPicker } from '../ui/color-picker';
import { ShadowControl, BorderControl } from '../ui/shadow-control';
import { FormField, FormSection, FormActions } from '../ui/form-field';
import { BadgePreview } from '../badges/badge-preview';

/**
 * AudioBadgeSettings Component
 * 
 * Settings page for configuring audio badge appearance
 * Based on the Aphrodite style guide
 * 
 * @returns {JSX.Element} AudioBadgeSettings component
 */
export const AudioBadgeSettings = () => {
  // State for badge settings
  const [settings, setSettings] = useState({
    codec_type: 'DOLBY ATMOS',
    position: 'top-right',
    size: 100, // percentage of original size
    margin: 16, // px
    z_index: 1,
    background_color: '#000000',
    background_transparency: 0.8,
    border_radius: 6, // px
    border_width: 1, // px
    border_color: '#FFFFFF',
    border_transparency: 0.5,
    shadow_toggle: true,
    shadow_color: 'rgba(0, 0, 0, 0.5)',
    shadow_blur_radius: 10, // px
    shadow_offset_x: 0, // px
    shadow_offset_y: 4, // px
  });
  
  // Available codec types
  const codecOptions = [
    { value: 'DOLBY ATMOS', label: 'Dolby Atmos' },
    { value: 'DTS-HD', label: 'DTS-HD' },
    { value: 'DOLBY DIGITAL', label: 'Dolby Digital' },
    { value: 'DTS', label: 'DTS' },
    { value: 'AAC', label: 'AAC' },
  ];
  
  // Handle setting changes
  const updateSetting = (key, value) => {
    setSettings((prev) => ({
      ...prev,
      [key]: value,
    }));
  };
  
  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    // Save settings logic would go here
    alert('Settings saved successfully!');
  };
  
  // Reset to defaults
  const handleReset = () => {
    setSettings({
      codec_type: 'DOLBY ATMOS',
      position: 'top-right',
      size: 100,
      margin: 16,
      z_index: 1,
      background_color: '#000000',
      background_transparency: 0.8,
      border_radius: 6,
      border_width: 1,
      border_color: '#FFFFFF',
      border_transparency: 0.5,
      shadow_toggle: true,
      shadow_color: 'rgba(0, 0, 0, 0.5)',
      shadow_blur_radius: 10,
      shadow_offset_x: 0,
      shadow_offset_y: 4,
    });
  };
  
  return (
    <div>
      <div className="mb-section">
        <H2>Audio Badge Settings</H2>
        <BodyLarge className="text-neutral mt-micro">
          Configure the appearance of your Audio Badges.
        </BodyLarge>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-default">
        <div className="lg:col-span-2">
          <form onSubmit={handleSubmit}>
            <Card>
              <CardHeader>
                <CardTitle>Audio Badge Settings</CardTitle>
              </CardHeader>
              <CardContent className="space-y-section">
                <FormSection title="Audio Codec Type">
                  <div className="w-full max-w-sm">
                    <Select
                      value={settings.codec_type}
                      onValueChange={(value) => updateSetting('codec_type', value)}
                      options={codecOptions}
                      placeholder="Select codec type"
                    />
                  </div>
                </FormSection>
                
                <FormSection title="Position">
                  <PositionGrid
                    value={settings.position}
                    onChange={(value) => updateSetting('position', value)}
                  />
                </FormSection>
                
                <FormSection>
                  <FormField 
                    label={`Size (${settings.size}%)`}
                    description="Percentage of original size"
                  >
                    <Slider
                      min={50}
                      max={200}
                      value={[settings.size]}
                      onValueChange={(value) => updateSetting('size', value[0])}
                      step={5}
                    />
                  </FormField>
                  
                  <FormField 
                    label={`Margin (${settings.margin}px)`}
                    description="Distance from poster edge"
                  >
                    <Slider
                      min={0}
                      max={50}
                      value={[settings.margin]}
                      onValueChange={(value) => updateSetting('margin', value[0])}
                      step={2}
                    />
                  </FormField>
                  
                  <FormField 
                    label={`Z-Index (${settings.z_index})`}
                    description="Layer position"
                  >
                    <Slider
                      min={0}
                      max={10}
                      value={[settings.z_index]}
                      onValueChange={(value) => updateSetting('z_index', value[0])}
                      step={1}
                    />
                  </FormField>
                </FormSection>
                
                <FormSection title="Appearance">
                  <FormField 
                    label="Background"
                  >
                    <div className="flex gap-small items-end">
                      <div className="flex-1">
                        <ColorPicker
                          value={settings.background_color}
                          onChange={(value) => updateSetting('background_color', value)}
                        />
                      </div>
                      
                      <div className="flex-1">
                        <Label className="mb-micro block">
                          Transparency ({Math.round(settings.background_transparency * 100)}%)
                        </Label>
                        <input
                          type="range"
                          min="0"
                          max="1"
                          step="0.01"
                          value={settings.background_transparency}
                          onChange={(e) => updateSetting('background_transparency', parseFloat(e.target.value))}
                          className="w-full h-1.5 bg-bg-light dark:bg-[#2E2E3E] rounded-full appearance-none cursor-pointer"
                        />
                      </div>
                    </div>
                  </FormField>
                  
                  <BorderControl
                    width={settings.border_width}
                    onWidthChange={(value) => updateSetting('border_width', value)}
                    radius={settings.border_radius}
                    onRadiusChange={(value) => updateSetting('border_radius', value)}
                    color={settings.border_color}
                    onColorChange={(value) => updateSetting('border_color', value)}
                    transparency={settings.border_transparency}
                    onTransparencyChange={(value) => updateSetting('border_transparency', value)}
                  />
                  
                  <ShadowControl
                    enabled={settings.shadow_toggle}
                    onEnabledChange={(value) => updateSetting('shadow_toggle', value)}
                    color={settings.shadow_color}
                    onColorChange={(value) => updateSetting('shadow_color', value)}
                    blurRadius={settings.shadow_blur_radius}
                    onBlurRadiusChange={(value) => updateSetting('shadow_blur_radius', value)}
                    offsetX={settings.shadow_offset_x}
                    onOffsetXChange={(value) => updateSetting('shadow_offset_x', value)}
                    offsetY={settings.shadow_offset_y}
                    onOffsetYChange={(value) => updateSetting('shadow_offset_y', value)}
                  />
                </FormSection>
                
                <FormActions>
                  <Button
                    type="button"
                    variant="secondary"
                    onClick={handleReset}
                  >
                    Reset to Defaults
                  </Button>
                  
                  <Button
                    type="submit"
                  >
                    Save Settings
                  </Button>
                </FormActions>
              </CardContent>
            </Card>
          </form>
        </div>
        
        <div>
          <BadgePreview
            settings={settings}
            type="audio"
            codecType={settings.codec_type}
          />
        </div>
      </div>
    </div>
  );
};

export default AudioBadgeSettings;
