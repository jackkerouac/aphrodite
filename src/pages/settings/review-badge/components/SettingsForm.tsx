import React from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { ReviewBadgeSettings } from '../hooks/useReviewBadgeSettings';

// Import subcomponents
import PositionSelector from './PositionSelector';
import LayoutSelector from './LayoutSelector';
import SourceSelector from './SourceSelector';
import AppearanceControls from './AppearanceControls';
import FontControls from './FontControls';
import LogoControls from './LogoControls';
import ShadowControls from './ShadowControls';

interface SettingsFormProps {
  settings: ReviewBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleNumberChange: (key: string, value: number) => void;
  handleColorChange: (key: string, value: string) => void;
  handleToggleChange: (key: string, value: boolean) => void;
  handleSelectChange: (key: string, value: string) => void;
  handleArrayChange: (key: string, value: string[]) => void;
  handlePositionChange: (value: string) => void;
  onSubmit: (e: React.FormEvent) => Promise<void>;
  saving: boolean;
  isSaveDisabled: boolean;
}

const SettingsForm: React.FC<SettingsFormProps> = ({
  settings,
  handleChange,
  handleNumberChange,
  handleColorChange,
  handleToggleChange,
  handleSelectChange,
  handleArrayChange,
  handlePositionChange,
  onSubmit,
  saving,
  isSaveDisabled
}) => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-4">
        <CardTitle>Review Badge Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-8" onSubmit={(e) => { e.preventDefault(); onSubmit(e); }}>
          <Tabs defaultValue="general" className="w-full">
            <TabsList className="grid grid-cols-4 mb-4">
              <TabsTrigger value="general">General</TabsTrigger>
              <TabsTrigger value="appearance">Appearance</TabsTrigger>
              <TabsTrigger value="text">Text</TabsTrigger>
              <TabsTrigger value="shadow">Shadow</TabsTrigger>
            </TabsList>
            
            <TabsContent value="general" className="space-y-6">
              {/* Position Selector */}
              <PositionSelector
                position={settings.position}
                handlePositionChange={handlePositionChange}
              />

              {/* Layout Selector */}
              <LayoutSelector
                layout={settings.badge_layout}
                handleSelectChange={(value) => handleSelectChange('badge_layout', value)}
              />

              {/* Source Selector */}
              <SourceSelector
                displaySources={settings.display_sources}
                sourceOrder={settings.source_order}
                handleArrayChange={handleArrayChange}
              />

              {/* Size and Spacing Controls */}
              <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Badge Size (%)</label>
                    <input
                      type="range"
                      name="size"
                      min="50"
                      max="200"
                      step="5"
                      value={settings.size}
                      onChange={handleChange}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs">
                      <span>50%</span>
                      <span>{settings.size}%</span>
                      <span>200%</span>
                    </div>
                  </div>
                  <div className="space-y-2">
                    <label className="text-sm font-medium">Margin (px)</label>
                    <input
                      type="range"
                      name="margin"
                      min="0"
                      max="50"
                      step="1"
                      value={settings.margin}
                      onChange={handleChange}
                      className="w-full"
                    />
                    <div className="flex justify-between text-xs">
                      <span>0px</span>
                      <span>{settings.margin}px</span>
                      <span>50px</span>
                    </div>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-sm font-medium">Spacing Between Badges (px)</label>
                  <input
                    type="range"
                    name="spacing"
                    min="0"
                    max="30"
                    step="1"
                    value={settings.spacing}
                    onChange={handleChange}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs">
                    <span>0px</span>
                    <span>{settings.spacing}px</span>
                    <span>30px</span>
                  </div>
                </div>
              </div>

              {/* Logo Controls */}
              <LogoControls
                settings={settings}
                handleToggleChange={handleToggleChange}
                handleNumberChange={handleNumberChange}
                handleSelectChange={handleSelectChange}
              />
            </TabsContent>
            
            <TabsContent value="appearance" className="space-y-6">
              {/* Appearance Controls */}
              <AppearanceControls
                settings={settings}
                handleChange={handleChange}
                handleColorChange={handleColorChange}
              />

              {/* Z-Index Control */}
              <div className="space-y-2">
                <label className="text-sm font-medium">Z-Index (Stacking Order)</label>
                <input
                  type="range"
                  name="z_index"
                  min="0"
                  max="10"
                  step="1"
                  value={settings.z_index}
                  onChange={handleChange}
                  className="w-full"
                />
                <div className="flex justify-between text-xs">
                  <span>0</span>
                  <span>{settings.z_index}</span>
                  <span>10</span>
                </div>
              </div>
            </TabsContent>
            
            <TabsContent value="text" className="space-y-6">
              {/* Font Controls */}
              <FontControls
                settings={settings}
                handleChange={handleChange}
                handleSelectChange={handleSelectChange}
                handleColorChange={handleColorChange}
                handleNumberChange={handleNumberChange}
              />
            </TabsContent>
            
            <TabsContent value="shadow" className="space-y-6">
              {/* Shadow Controls */}
              <ShadowControls
                settings={settings}
                handleChange={handleChange}
                handleColorChange={handleColorChange}
                handleToggleChange={handleToggleChange}
              />
            </TabsContent>
          </Tabs>
        </form>
      </CardContent>
      <CardFooter>
        <Button
          type="submit"
          className="w-full"
          disabled={saving || isSaveDisabled}
          onClick={onSubmit}
        >
          {saving ? (
            <>
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
              Saving...
            </>
          ) : (
            'Save Settings'
          )}
        </Button>
      </CardFooter>
    </Card>
  );
};

export default SettingsForm;
