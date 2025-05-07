import React from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { BadgeDisplaySettings } from '../hooks/useBadgePreviewSettings';

interface BadgeTogglesProps {
  displaySettings: BadgeDisplaySettings;
  toggleBadge: (badge: keyof BadgeDisplaySettings) => void;
  loading: boolean;
}

const BadgeToggles: React.FC<BadgeTogglesProps> = ({
  displaySettings,
  toggleBadge,
  loading
}) => {
  return (
    <div className="space-y-4">
      <h3 className="text-lg font-medium">Badge Display</h3>
      <div className="space-y-3">

      <div className="flex items-center justify-between">
          <Label htmlFor="audioBadge" className="cursor-pointer">
            Audio Badge
          </Label>
          <Switch
            id="audioBadge"
            disabled={loading}
            checked={displaySettings.showAudioBadge}
            onCheckedChange={() => toggleBadge('showAudioBadge')}
          />
        </div>

        <div className="flex items-center justify-between">
          <Label htmlFor="resolutionBadge" className="cursor-pointer">
            Resolution Badge
          </Label>
          <Switch
            id="resolutionBadge"
            disabled={loading}
            checked={displaySettings.showResolutionBadge}
            onCheckedChange={() => toggleBadge('showResolutionBadge')}
          />
        </div>
        
        <div className="flex items-center justify-between">
          <Label htmlFor="reviewBadge" className="cursor-pointer">
            Review Badge
          </Label>
          <Switch
            id="reviewBadge"
            disabled={loading}
            checked={displaySettings.showReviewBadge}
            onCheckedChange={() => toggleBadge('showReviewBadge')}
          />
        </div>
      </div>
    </div>
  );
};

export default BadgeToggles;
