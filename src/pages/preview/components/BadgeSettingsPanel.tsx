import React from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { 
  AudioBadgeSettings, 
  ResolutionBadgeSettings, 
  ReviewBadgeSettings 
} from '@/types/unifiedBadgeSettings';
import { 
  AudioBadgeControls, 
  ResolutionBadgeControls, 
  ReviewBadgeControls 
} from '@/components/badges/unified';

interface BadgeSettingsPanelProps {
  audioBadge: AudioBadgeSettings | null;
  resolutionBadge: ResolutionBadgeSettings | null;
  reviewBadge: ReviewBadgeSettings | null;
  onAudioBadgeChange: (settings: AudioBadgeSettings) => void;
  onResolutionBadgeChange: (settings: ResolutionBadgeSettings) => void;
  onReviewBadgeChange: (settings: ReviewBadgeSettings) => void;
  activeTab?: string;
  onTabChange?: (tab: string) => void;
}

/**
 * Component for displaying and editing badge settings
 */
export const BadgeSettingsPanel: React.FC<BadgeSettingsPanelProps> = ({
  audioBadge,
  resolutionBadge,
  reviewBadge,
  onAudioBadgeChange,
  onResolutionBadgeChange,
  onReviewBadgeChange,
  activeTab = 'audio',
  onTabChange
}) => {
  const handleTabChange = (tab: string) => {
    if (onTabChange) {
      onTabChange(tab);
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <CardTitle>Badge Settings</CardTitle>
      </CardHeader>
      <CardContent>
        <Tabs 
          defaultValue={activeTab} 
          className="w-full"
          onValueChange={handleTabChange}
        >
          <TabsList className="grid grid-cols-3 mb-6">
            <TabsTrigger value="audio">Audio</TabsTrigger>
            <TabsTrigger value="resolution">Resolution</TabsTrigger>
            <TabsTrigger value="review">Review</TabsTrigger>
          </TabsList>
          
          <TabsContent value="audio" className="space-y-4">
            {audioBadge && (
              <AudioBadgeControls
                settings={audioBadge}
                onChange={onAudioBadgeChange}
              />
            )}
          </TabsContent>
          
          <TabsContent value="resolution" className="space-y-4">
            {resolutionBadge && (
              <ResolutionBadgeControls
                settings={resolutionBadge}
                onChange={onResolutionBadgeChange}
              />
            )}
          </TabsContent>
          
          <TabsContent value="review" className="space-y-4">
            {reviewBadge && (
              <ReviewBadgeControls
                settings={reviewBadge}
                onChange={onReviewBadgeChange}
              />
            )}
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
};

export default BadgeSettingsPanel;
