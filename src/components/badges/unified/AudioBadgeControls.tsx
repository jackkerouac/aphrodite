import React from 'react';
import { AudioBadgeSettings } from '@/types/unifiedBadgeSettings';
import BaseBadgeControls from './BaseBadgeControls';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { audioCodecOptions } from '@/utils/audioCodecUtils';

interface AudioBadgeControlsProps {
  settings: AudioBadgeSettings;
  onChange: (settings: AudioBadgeSettings) => void;
}

/**
 * Controls specific to Audio badges
 */
const AudioBadgeControls: React.FC<AudioBadgeControlsProps> = ({ settings, onChange }) => {
  // Handle change in audio-specific properties
  const handlePropertyChange = (key: keyof AudioBadgeSettings['properties'], value: any) => {
    onChange({
      ...settings,
      properties: {
        ...settings.properties,
        [key]: value
      }
    });
  };

  return (
    <BaseBadgeControls
      settings={settings}
      onChange={onChange}
      badgeType="audio"
    >
      {/* Audio-specific controls */}
      <div className="space-y-2 mb-4 border-t border-gray-200 pt-4 mt-4">
        <Label htmlFor="codec_type">Audio Codec</Label>
        <Select
          value={settings.properties.codec_type || 'dolby_atmos'}
          onValueChange={(value) => handlePropertyChange('codec_type', value)}
        >
          <SelectTrigger id="codec_type">
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
    </BaseBadgeControls>
  );
};

export default AudioBadgeControls;
