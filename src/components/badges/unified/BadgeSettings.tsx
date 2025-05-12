import React, { useState } from 'react';
import { 
  UnifiedBadgeSettings, 
  AudioBadgeSettings, 
  ResolutionBadgeSettings, 
  ReviewBadgeSettings,
  DEFAULT_AUDIO_BADGE_SETTINGS,
  DEFAULT_RESOLUTION_BADGE_SETTINGS,
  DEFAULT_REVIEW_BADGE_SETTINGS
} from '@/types/unifiedBadgeSettings';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import AudioBadgeControls from './AudioBadgeControls';
import ResolutionBadgeControls from './ResolutionBadgeControls';
import ReviewBadgeControls from './ReviewBadgeControls';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';

interface BadgeSettingsProps {
  audioBadge: AudioBadgeSettings | null;
  resolutionBadge: ResolutionBadgeSettings | null;
  reviewBadge: ReviewBadgeSettings | null;
  onAudioBadgeChange: (settings: AudioBadgeSettings | null) => void;
  onResolutionBadgeChange: (settings: ResolutionBadgeSettings | null) => void;
  onReviewBadgeChange: (settings: ReviewBadgeSettings | null) => void;
  className?: string;
}

/**
 * Main component for managing badge settings with tabs for each badge type
 */
const BadgeSettings: React.FC<BadgeSettingsProps> = ({
  audioBadge,
  resolutionBadge,
  reviewBadge,
  onAudioBadgeChange,
  onResolutionBadgeChange,
  onReviewBadgeChange,
  className = ''
}) => {
  // Track which tab is currently active
  const [activeTab, setActiveTab] = useState<string>('audio');

  // Determine which badges are enabled
  const isAudioEnabled = audioBadge !== null;
  const isResolutionEnabled = resolutionBadge !== null;
  const isReviewEnabled = reviewBadge !== null;

  // Handle toggle for each badge type
  const handleAudioToggle = (enabled: boolean) => {
    if (enabled) {
      onAudioBadgeChange(DEFAULT_AUDIO_BADGE_SETTINGS);
    } else {
      onAudioBadgeChange(null);
    }
  };

  const handleResolutionToggle = (enabled: boolean) => {
    if (enabled) {
      onResolutionBadgeChange(DEFAULT_RESOLUTION_BADGE_SETTINGS);
    } else {
      onResolutionBadgeChange(null);
    }
  };

  const handleReviewToggle = (enabled: boolean) => {
    if (enabled) {
      onReviewBadgeChange(DEFAULT_REVIEW_BADGE_SETTINGS);
    } else {
      onReviewBadgeChange(null);
    }
  };

  return (
    <div className={`badge-settings ${className}`}>
      <Tabs
        defaultValue="audio"
        value={activeTab}
        onValueChange={setActiveTab}
        className="w-full"
      >
        <div className="flex justify-between items-center mb-4">
          <TabsList>
            <TabsTrigger 
              value="audio" 
              onClick={() => setActiveTab('audio')}
              className="flex items-center gap-2"
            >
              <span>Audio</span>
              {isAudioEnabled && (
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              )}
            </TabsTrigger>
            <TabsTrigger 
              value="resolution" 
              onClick={() => setActiveTab('resolution')}
              className="flex items-center gap-2"
            >
              <span>Resolution</span>
              {isResolutionEnabled && (
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              )}
            </TabsTrigger>
            <TabsTrigger 
              value="review" 
              onClick={() => setActiveTab('review')}
              className="flex items-center gap-2"
            >
              <span>Review</span>
              {isReviewEnabled && (
                <span className="w-2 h-2 bg-green-500 rounded-full"></span>
              )}
            </TabsTrigger>
          </TabsList>
          
          {/* Toggle switch for the active badge */}
          <div className="flex items-center space-x-2">
            <Switch
              id={`${activeTab}-badge-toggle`}
              checked={
                (activeTab === 'audio' && isAudioEnabled) ||
                (activeTab === 'resolution' && isResolutionEnabled) ||
                (activeTab === 'review' && isReviewEnabled)
              }
              onCheckedChange={(checked) => {
                switch (activeTab) {
                  case 'audio':
                    handleAudioToggle(checked);
                    break;
                  case 'resolution':
                    handleResolutionToggle(checked);
                    break;
                  case 'review':
                    handleReviewToggle(checked);
                    break;
                }
              }}
            />
            <Label htmlFor={`${activeTab}-badge-toggle`}>Enable Badge</Label>
          </div>
        </div>

        {/* Tab content for each badge type */}
        <TabsContent value="audio" className="mt-2">
          {isAudioEnabled && audioBadge ? (
            <AudioBadgeControls
              settings={audioBadge}
              onChange={onAudioBadgeChange}
            />
          ) : (
            <div className="p-4 text-center text-gray-500 border border-dashed border-gray-300 rounded-lg">
              <p>Audio badge is disabled. Enable it to configure settings.</p>
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="resolution" className="mt-2">
          {isResolutionEnabled && resolutionBadge ? (
            <ResolutionBadgeControls
              settings={resolutionBadge}
              onChange={onResolutionBadgeChange}
            />
          ) : (
            <div className="p-4 text-center text-gray-500 border border-dashed border-gray-300 rounded-lg">
              <p>Resolution badge is disabled. Enable it to configure settings.</p>
            </div>
          )}
        </TabsContent>
        
        <TabsContent value="review" className="mt-2">
          {isReviewEnabled && reviewBadge ? (
            <ReviewBadgeControls
              settings={reviewBadge}
              onChange={onReviewBadgeChange}
            />
          ) : (
            <div className="p-4 text-center text-gray-500 border border-dashed border-gray-300 rounded-lg">
              <p>Review badge is disabled. Enable it to configure settings.</p>
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default BadgeSettings;
