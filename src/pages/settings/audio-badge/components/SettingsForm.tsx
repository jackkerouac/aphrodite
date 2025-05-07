import React, { useCallback } from 'react';
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { AudioBadgeSettings } from '../hooks/useAudioBadgeSettings';

// Import subcomponents
import AudioCodecSelector from './AudioCodecSelector';
import PositionSelector from './PositionSelector';
import SizeControls from './SizeControls';
import AppearanceControls from './AppearanceControls';
import ShadowControls from './ShadowControls';

interface SettingsFormProps {
  settings: AudioBadgeSettings;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleColorChange: (key: string, value: string) => void;
  handleToggleChange: (key: string, value: boolean) => void;
  handlePositionChange: (value: string) => void;
  handleAudioCodecChange: (value: string) => void;
  selectedAudioCodec: string;
  onSubmit: (e: React.FormEvent) => Promise<void>;
  saving: boolean;
  isSaveDisabled: boolean;
  audioCodecOptions: string[];
}

const SettingsForm: React.FC<SettingsFormProps> = ({
  settings,
  handleChange,
  handleColorChange,
  handleToggleChange,
  handlePositionChange,
  handleAudioCodecChange,
  selectedAudioCodec,
  onSubmit,
  saving,
  isSaveDisabled,
  audioCodecOptions
}) => {
  return (
    <Card className="h-full">
      <CardHeader className="pb-4">
        <CardTitle>Audio Badge Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <form className="space-y-8" onSubmit={(e) => { e.preventDefault(); onSubmit(e); }}>
          {/* Audio Codec Selector */}
          <div className="space-y-6">
            <AudioCodecSelector
              selectedAudioCodec={selectedAudioCodec}
              handleAudioCodecChange={handleAudioCodecChange}
              audioCodecOptions={audioCodecOptions}
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

export default SettingsForm;