import React, { useCallback } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { ResolutionBadgeSettings } from './resolution-badge/hooks/useResolutionBadgeSettings';

// Import subcomponents
import ResolutionSelector from './resolution-badge/components/ResolutionSelector';
import PositionSelector from './resolution-badge/components/PositionSelector';
import SizeControls from './resolution-badge/components/SizeControls';
import AppearanceControls from './resolution-badge/components/AppearanceControls';
import ShadowControls from './resolution-badge/components/ShadowControls';

interface SettingsFormProps {
  settings: ResolutionBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleColorChange: (key: string, value: string) => void;
  handleToggleChange: (key: string, value: boolean) => void;
  handlePositionChange: (value: string) => void;
  handleResolutionChange: (value: string) => void;
  selectedResolution: string;
  onSubmit: (e: React.FormEvent) => Promise<void>;
  saving: boolean;
  isSaveDisabled: boolean;
  resolutionOptions: string[];
}

const DesignResolutionBadgeSettings: React.FC<SettingsFormProps> = ({
  settings,
  handleChange,
  handleColorChange,
  handleToggleChange,
  handlePositionChange,
  handleResolutionChange,
  selectedResolution,
  onSubmit,
  saving,
  isSaveDisabled,
  resolutionOptions
}) => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-4">
        <CardTitle>Resolution Badge Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-8" onSubmit={(e) => { e.preventDefault(); onSubmit(e); }}>
          {/* Resolution Selector */}
          <div className="space-y-6">
            <ResolutionSelector
              selectedResolution={selectedResolution}
              handleResolutionChange={handleResolutionChange}
              resolutionOptions={resolutionOptions}
            />

            {/* Position Selector */}
            <PositionSelector
              position={settings.position}
              handlePositionChange={handlePositionChange}
            />

            {/* Size Controls */}
            <SizeControls
              settings={settings}
              handleChange={handleChange}
            />

            {/* Appearance Controls */}
            <AppearanceControls
              settings={settings}
              handleChange={handleChange}
              handleColorChange={handleColorChange}
            />

            {/* Shadow Controls */}
            <ShadowControls
              settings={settings}
              handleChange={handleChange}
              handleColorChange={handleColorChange}
              handleToggleChange={handleToggleChange}
            />
          </div>
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

export default DesignResolutionBadgeSettings;
