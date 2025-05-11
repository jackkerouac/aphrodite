import { useState, useEffect } from "react";
import { useBadgeSettings } from "@/hooks/useBadgeSettings";
import { AudioBadgeSettings } from "@/components/badges/types/AudioBadge";
import { ResolutionBadgeSettings } from "@/components/badges/types/ResolutionBadge";
import { ReviewBadgeSettings } from "@/components/badges/types/ReviewBadge";
import { BadgePosition } from "@/components/badges/PositionSelector";
import { convertLegacyPosition } from "@/lib/utils/badge-position";
import { 
  defaultAudioBadgeSettings,
  defaultResolutionBadgeSettings, 
  defaultReviewBadgeSettings 
} from "../constants/defaultBadgeSettings";

export interface BadgeState {
  activeBadgeType: string | null;
  audioBadgeSettings: AudioBadgeSettings;
  resolutionBadgeSettings: ResolutionBadgeSettings;
  reviewBadgeSettings: ReviewBadgeSettings;
  saveAudioBadgeSettings: (settings: AudioBadgeSettings) => void;
  saveResolutionBadgeSettings: (settings: ResolutionBadgeSettings) => void;
  saveReviewBadgeSettings: (settings: ReviewBadgeSettings) => void;
  setActiveBadgeType: (type: string) => void;
  handleBadgePositionChange: (type: string, position: BadgePosition) => void;
  loading: boolean;
  updatePreview: () => void;
}

export const useBadgeState = (
  userId: string = "123",
  updateCanvasCallback: () => void
): BadgeState => {
  // Active badge type for editing
  const [activeBadgeType, setActiveBadgeType] = useState<string | null>("audio");
  
  // Get badge settings for each type using our hook
  const { 
    badgeSettings: audioBadgeSettings, 
    saveBadgeSettings: saveAudioBadgeSettings,
    isLoading: isLoadingAudio
  } = useBadgeSettings<AudioBadgeSettings>(userId, "audio");
  
  const { 
    badgeSettings: resolutionBadgeSettings, 
    saveBadgeSettings: saveResolutionBadgeSettings,
    isLoading: isLoadingResolution
  } = useBadgeSettings<ResolutionBadgeSettings>(userId, "resolution");
  
  const { 
    badgeSettings: reviewBadgeSettings, 
    saveBadgeSettings: saveReviewBadgeSettings,
    isLoading: isLoadingReview
  } = useBadgeSettings<ReviewBadgeSettings>(userId, "review");

  // Overall loading state
  const [loading, setLoading] = useState(true);

  // Update loading state when all settings are loaded
  useEffect(() => {
    setLoading(isLoadingAudio || isLoadingResolution || isLoadingReview);
  }, [isLoadingAudio, isLoadingResolution, isLoadingReview]);
  
  // Debug output when settings change
  useEffect(() => {
    if (!loading) {
      console.log('Audio badge settings loaded:', audioBadgeSettings);
      console.log('Resolution badge settings loaded:', resolutionBadgeSettings);
      console.log('Review badge settings loaded:', reviewBadgeSettings);
    }
  }, [loading, audioBadgeSettings, resolutionBadgeSettings, reviewBadgeSettings]);
  
  // Handle badge type selection
  const handleBadgeTypeChange = (type: string) => {
    setActiveBadgeType(type);
    updateCanvasCallback();
  };

  // Handle badge position changes
  const handleBadgePositionChange = (type: string, position: BadgePosition) => {
    // Update the position for the appropriate badge type
    switch (type) {
      case "audio":
        saveAudioBadgeSettings({
          ...(audioBadgeSettings || defaultAudioBadgeSettings),
          position
        });
        break;
      case "resolution":
        saveResolutionBadgeSettings({
          ...(resolutionBadgeSettings || defaultResolutionBadgeSettings),
          position
        });
        break;
      case "review":
        saveReviewBadgeSettings({
          ...(reviewBadgeSettings || defaultReviewBadgeSettings),
          position
        });
        break;
    }
    updateCanvasCallback();
  };

  // Function to update the preview immediately
  const updatePreview = () => {
    updateCanvasCallback();
  };

  // Create wrapped save functions that force immediate updates
  const saveAudioBadgeSettingsWithUpdate = (settings: AudioBadgeSettings) => {
    saveAudioBadgeSettings(settings);
    // Force immediate update
    requestAnimationFrame(updatePreview);
  };
  
  const saveResolutionBadgeSettingsWithUpdate = (settings: ResolutionBadgeSettings) => {
    saveResolutionBadgeSettings(settings);
    // Force immediate update
    requestAnimationFrame(updatePreview);
  };
  
  const saveReviewBadgeSettingsWithUpdate = (settings: ReviewBadgeSettings) => {
    saveReviewBadgeSettings(settings);
    // Force immediate update
    requestAnimationFrame(updatePreview);
  };

  return {
    activeBadgeType,
    audioBadgeSettings: audioBadgeSettings || defaultAudioBadgeSettings,
    resolutionBadgeSettings: resolutionBadgeSettings || defaultResolutionBadgeSettings,
    reviewBadgeSettings: reviewBadgeSettings || defaultReviewBadgeSettings,
    saveAudioBadgeSettings: saveAudioBadgeSettingsWithUpdate,
    saveResolutionBadgeSettings: saveResolutionBadgeSettingsWithUpdate,
    saveReviewBadgeSettings: saveReviewBadgeSettingsWithUpdate,
    setActiveBadgeType: handleBadgeTypeChange,
    handleBadgePositionChange,
    loading,
    updatePreview
  };
};
