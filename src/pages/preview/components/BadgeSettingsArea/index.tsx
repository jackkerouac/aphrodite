import * as React from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { FileSliders } from "lucide-react";
import BadgeToggles from "../BadgeToggles";
import BadgeControls from "@/components/badges/BadgeControls";
import SaveBadgeSettingsButton from "../SaveBadgeSettingsButton";
import { AudioBadgeSettings } from "@/components/badges/types/AudioBadge";
import { ResolutionBadgeSettings } from "@/components/badges/types/ResolutionBadge";
import { ReviewBadgeSettings } from "@/components/badges/types/ReviewBadge";

interface BadgeSettingsAreaProps {
  displaySettings: {
    showAudioBadge: boolean;
    showResolutionBadge: boolean;
    showReviewBadge: boolean;
  };
  toggleBadge: (type: string) => void;
  loading: boolean;
  badgeSettingsLoading: boolean;
  onBadgeTypeChange: (type: string) => void;
  saveHandlers: {
    audio: (settings: AudioBadgeSettings) => void;
    resolution: (settings: ResolutionBadgeSettings) => void;
    review: (settings: ReviewBadgeSettings) => void;
  };
  audioBadgeSettings: AudioBadgeSettings;
  resolutionBadgeSettings: ResolutionBadgeSettings;
  reviewBadgeSettings: ReviewBadgeSettings;
}

const BadgeSettingsArea: React.FC<BadgeSettingsAreaProps> = ({
  displaySettings,
  toggleBadge,
  loading,
  badgeSettingsLoading,
  onBadgeTypeChange,
  saveHandlers,
  audioBadgeSettings,
  resolutionBadgeSettings,
  reviewBadgeSettings
}) => {
  return (
    <Card className="h-full">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <FileSliders className="w-5 h-5" />
          Badge Settings
        </CardTitle>
        <CardDescription>Customize badge appearance</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Badge Type Toggles */}
          <div className="space-y-3">
            <h3 className="text-lg font-medium">Display Badges</h3>
            <div className="flex flex-col gap-3">
              <BadgeToggles
                displaySettings={displaySettings}
                toggleBadge={toggleBadge}
                loading={loading || badgeSettingsLoading}
              />
            </div>
          </div>

          {/* Badge Controls */}
          <div className="space-y-3">
            <h3 className="text-lg font-medium">Badge Settings</h3>
            <BadgeControls 
              userId="123" 
              onBadgeTypeChange={onBadgeTypeChange}
              initialBadgeType="audio"
              saveHandlers={saveHandlers}
            />
          </div>

          {/* Save Badge Settings Button */}
          <div className="space-y-3 pt-4">
            <h3 className="text-lg font-medium">Save Badge Settings</h3>
            <SaveBadgeSettingsButton 
              displaySettings={displaySettings}
              audioBadgeSettings={audioBadgeSettings}
              resolutionBadgeSettings={resolutionBadgeSettings}
              reviewBadgeSettings={reviewBadgeSettings}
              userId="123"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default BadgeSettingsArea;
