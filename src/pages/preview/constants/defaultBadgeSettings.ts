import { getResolutionDisplayName, getResolutionImagePath } from "@/utils/resolutionUtils";
import { AudioBadgeSettings } from "@/components/badges/types/AudioBadge";
import { ResolutionBadgeSettings } from "@/components/badges/types/ResolutionBadge";
import { ReviewBadgeSettings } from "@/components/badges/types/ReviewBadge";

// Default settings for each badge type if hook fails to load
export const defaultAudioBadgeSettings: AudioBadgeSettings = {
  type: 'audio',
  size: 80,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  textColor: '#FFFFFF',
  codecType: 'Dolby Atmos',
  position: {
    percentX: 5,
    percentY: 5,
  },
};

export const defaultResolutionBadgeSettings: ResolutionBadgeSettings = {
  type: 'resolution',
  size: 100,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  textColor: '#FFFFFF',
  resolutionType: '1080p',
  borderRadius: 4,
  borderWidth: 1,
  borderColor: '#FFFFFF',
  borderOpacity: 0.8,
  shadowEnabled: false,
  directImageRender: false,
  // Use utility functions for resolution image path and display name
  getResolutionImagePath: getResolutionImagePath,
  getResolutionDisplayName: getResolutionDisplayName,
  position: {
    percentX: 5,
    percentY: 15,
  },
};

export const defaultReviewBadgeSettings: ReviewBadgeSettings = {
  type: 'review',
  size: 100,
  backgroundColor: '#000000',
  backgroundOpacity: 0.7,
  textColor: '#FFFFFF',
  displayFormat: 'horizontal',
  maxSourcesToShow: 2,
  showDividers: true,
  sources: [
    { name: 'IMDB', rating: 8.5, outOf: 10 },
    { name: 'RT', rating: 90, outOf: 100 }
  ],
  position: {
    percentX: 5,
    percentY: 25,
  },
};
