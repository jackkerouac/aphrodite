import React from 'react';
import { badgeDescriptions } from '../constants';
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
      <div className="space-y-3">
        <div className="flex items-center space-x-2 justify-start">
          <Switch
            id="audioBadge"
            disabled={loading}
            checked={displaySettings.showAudioBadge}
            onCheckedChange={() => toggleBadge('showAudioBadge')}
          />
          <div>
            <Label htmlFor="audioBadge" className="cursor-pointer">
              Audio Badge
            </Label>
            <p className="text-xs text-muted-foreground">
              {badgeDescriptions.showAudioBadge}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 justify-start">
          <Switch
            id="resolutionBadge"
            disabled={loading}
            checked={displaySettings.showResolutionBadge}
            onCheckedChange={() => toggleBadge('showResolutionBadge')}
          />
          <div>
            <Label htmlFor="resolutionBadge" className="cursor-pointer">
              Resolution Badge
            </Label>
            <p className="text-xs text-muted-foreground">
              {badgeDescriptions.showResolutionBadge}
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 justify-start">
          <Switch
            id="reviewBadge"
            disabled={loading}
            checked={displaySettings.showReviewBadge}
            onCheckedChange={() => toggleBadge('showReviewBadge')}
          />
          <div>
            <Label htmlFor="reviewBadge" className="cursor-pointer">
              Review Badge
            </Label>
            <p className="text-xs text-muted-foreground">
              {badgeDescriptions.showReviewBadge}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BadgeToggles;
