import React, { useEffect, useLayoutEffect, useRef } from 'react';
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
  // Create toggle handlers that explicitly log when triggered
  const handleAudioToggle = () => {
    console.log('Audio toggle clicked, current state:', displaySettings.showAudioBadge);
    toggleBadge('showAudioBadge');
  };

  const handleResolutionToggle = () => {
    console.log('Resolution toggle clicked, current state:', displaySettings.showResolutionBadge);
    toggleBadge('showResolutionBadge');
  };

  const handleReviewToggle = () => {
    console.log('Review toggle clicked, current state:', displaySettings.showReviewBadge);
    toggleBadge('showReviewBadge');
  };

  // Track when settings change and force UI update via ref counter
  const renderCountRef = useRef(0);
  
  // Force re-render with useLayoutEffect to ensure DOM is updated before browser paint
  useLayoutEffect(() => {
    renderCountRef.current += 1;
    console.log(`BadgeToggles re-rendering (${renderCountRef.current}) with settings:`, displaySettings);
  }, [displaySettings.showAudioBadge, displaySettings.showResolutionBadge, displaySettings.showReviewBadge]);
  
  return (
    <div className="space-y-4">
      <div className="space-y-3">
        {/* Audio Badge Toggle */}
        <div className="flex items-center space-x-2 justify-start">
          <Switch
            id="audioBadge"
            disabled={loading}
            checked={displaySettings.showAudioBadge}
            onCheckedChange={handleAudioToggle}
          />
          <div>
            <Label htmlFor="audioBadge" className="cursor-pointer">
              Audio Badge {displaySettings.showAudioBadge ? '(ON)' : '(OFF)'}
            </Label>
            <p className="text-xs text-muted-foreground">
              {badgeDescriptions.showAudioBadge}
            </p>
          </div>
        </div>

        {/* Resolution Badge Toggle */}
        <div className="flex items-center space-x-2 justify-start">
          <Switch
            id="resolutionBadge"
            disabled={loading}
            checked={displaySettings.showResolutionBadge}
            onCheckedChange={handleResolutionToggle}
          />
          <div>
            <Label htmlFor="resolutionBadge" className="cursor-pointer">
              Resolution Badge {displaySettings.showResolutionBadge ? '(ON)' : '(OFF)'}
            </Label>
            <p className="text-xs text-muted-foreground">
              {badgeDescriptions.showResolutionBadge}
            </p>
          </div>
        </div>

        {/* Review Badge Toggle */}
        <div className="flex items-center space-x-2 justify-start">
          <Switch
            id="reviewBadge"
            disabled={loading}
            checked={displaySettings.showReviewBadge}
            onCheckedChange={handleReviewToggle}
          />
          <div>
            <Label htmlFor="reviewBadge" className="cursor-pointer">
              Review Badge {displaySettings.showReviewBadge ? '(ON)' : '(OFF)'}
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
