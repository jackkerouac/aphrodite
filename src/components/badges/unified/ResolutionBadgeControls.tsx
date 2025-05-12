import React from 'react';
import { ResolutionBadgeSettings } from '@/types/unifiedBadgeSettings';
import BaseBadgeControls from './BaseBadgeControls';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { resolutionOptions } from '@/utils/resolutionUtils';

interface ResolutionBadgeControlsProps {
  settings: ResolutionBadgeSettings;
  onChange: (settings: ResolutionBadgeSettings) => void;
}

/**
 * Controls specific to Resolution badges
 */
const ResolutionBadgeControls: React.FC<ResolutionBadgeControlsProps> = ({ settings, onChange }) => {
  // Handle change in resolution-specific properties
  const handlePropertyChange = (key: keyof ResolutionBadgeSettings['properties'], value: any) => {
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
      badgeType="resolution"
    >
      {/* Resolution-specific controls */}
      <div className="space-y-2 mb-4 border-t border-gray-200 pt-4 mt-4">
        <Label htmlFor="resolution_type">Resolution</Label>
        <Select
          value={settings.properties.resolution_type || '4k'}
          onValueChange={(value) => handlePropertyChange('resolution_type', value)}
        >
          <SelectTrigger id="resolution_type">
            <SelectValue placeholder="Select resolution" />
          </SelectTrigger>
          <SelectContent>
            {resolutionOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <div className="text-xs text-gray-500 mt-1">
          The selected resolution will appear as an image in the badge
        </div>
      </div>
    </BaseBadgeControls>
  );
};

export default ResolutionBadgeControls;
