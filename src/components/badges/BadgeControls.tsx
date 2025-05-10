import React, { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useBadgeSettings } from "@/hooks/useBadgeSettings";
import AudioBadgeControls from './controls/AudioBadgeControls';
import ResolutionBadgeControls from './controls/ResolutionBadgeControls';
import ReviewBadgeControls from './controls/ReviewBadgeControls';
import { AudioBadgeSettings } from './types/AudioBadge';
import { ResolutionBadgeSettings } from './types/ResolutionBadge';
import { ReviewBadgeSettings } from './types/ReviewBadge';

interface BadgeControlsProps {
  userId: string;
  onBadgeTypeChange?: (type: string) => void;
  initialBadgeType?: string;
  saveHandlers?: {
    audio: (settings: AudioBadgeSettings) => void;
    resolution: (settings: ResolutionBadgeSettings) => void;
    review: (settings: ReviewBadgeSettings) => void;
  };
}

const BadgeControls: React.FC<BadgeControlsProps> = ({ 
  userId, 
  onBadgeTypeChange, 
  initialBadgeType = "audio",
  saveHandlers
}) => {
  const [activeTab, setActiveTab] = useState<string>(initialBadgeType);
  
  // Get badge settings for each type
  const { 
    badgeSettings: audioBadgeSettings, 
    saveBadgeSettings: saveAudioBadgeSettings 
  } = useBadgeSettings<AudioBadgeSettings>(userId, "audio");
  
  const { 
    badgeSettings: resolutionBadgeSettings, 
    saveBadgeSettings: saveResolutionBadgeSettings 
  } = useBadgeSettings<ResolutionBadgeSettings>(userId, "resolution");
  
  const { 
    badgeSettings: reviewBadgeSettings, 
    saveBadgeSettings: saveReviewBadgeSettings 
  } = useBadgeSettings<ReviewBadgeSettings>(userId, "review");

  // Handle tab change
  const handleTabChange = (value: string) => {
    setActiveTab(value);
    if (onBadgeTypeChange) {
      onBadgeTypeChange(value);
    }
  };

  // Notify parent when tab changes
  useEffect(() => {
    if (onBadgeTypeChange) {
      onBadgeTypeChange(activeTab);
    }
  }, [activeTab, onBadgeTypeChange]);

  return (
    <Tabs
      value={activeTab}
      onValueChange={handleTabChange}
      className="w-full"
    >
      <TabsList className="grid grid-cols-3 mb-4">
        <TabsTrigger value="audio">Audio</TabsTrigger>
        <TabsTrigger value="resolution">Resolution</TabsTrigger>
        <TabsTrigger value="review">Review</TabsTrigger>
      </TabsList>
      
      <TabsContent value="audio" className="space-y-4">
        <AudioBadgeControls 
          settings={audioBadgeSettings as AudioBadgeSettings} 
          onChange={saveHandlers?.audio || saveAudioBadgeSettings}
        />
      </TabsContent>
      
      <TabsContent value="resolution" className="space-y-4">
        <ResolutionBadgeControls 
          settings={resolutionBadgeSettings as ResolutionBadgeSettings} 
          onChange={saveHandlers?.resolution || saveResolutionBadgeSettings}
        />
      </TabsContent>
      
      <TabsContent value="review" className="space-y-4">
        <ReviewBadgeControls 
          settings={reviewBadgeSettings as ReviewBadgeSettings} 
          onChange={saveHandlers?.review || saveReviewBadgeSettings}
        />
      </TabsContent>
    </Tabs>
  );
};

export default BadgeControls;