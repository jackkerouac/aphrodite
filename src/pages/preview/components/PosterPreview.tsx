import React from 'react';
import { BadgeDisplaySettings } from '../hooks/useBadgePreviewSettings';
import { getBadgePositionStyles } from '@/lib/utils/badge-position';

interface PosterPreviewProps {
  posterImage: string;
  displaySettings: BadgeDisplaySettings;
  resolutionBadgeSettings: any | null;
  audioBadgeSettings: any | null;
  reviewBadgeSettings: any | null;
  loading: boolean;
}

const PosterPreview: React.FC<PosterPreviewProps> = ({
  posterImage,
  displaySettings,
  resolutionBadgeSettings,
  audioBadgeSettings,
  reviewBadgeSettings,
  loading
}) => {
  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        <p className="mt-4 text-sm text-muted-foreground">Loading badge settings...</p>
      </div>
    );
  }

  return (
    <div className="relative flex justify-center items-center h-full">
      <div className="relative">
        <img
          src={posterImage}
          alt="Poster Preview"
          className="max-w-full h-auto object-contain"
        />
        
        {/* Resolution Badge */}
        {displaySettings.showResolutionBadge && resolutionBadgeSettings && (
          <div
            className="absolute bg-black bg-opacity-80 text-white px-2 py-1 rounded"
            style={{
              ...getBadgePositionStyles(resolutionBadgeSettings.position, resolutionBadgeSettings.margin),
              fontSize: `${resolutionBadgeSettings.size / 10}rem`,
              backgroundColor: `${resolutionBadgeSettings.backgroundColor}${Math.round(resolutionBadgeSettings.backgroundOpacity * 255).toString(16)}`,
              borderRadius: `${resolutionBadgeSettings.borderRadius}px`,
              borderWidth: `${resolutionBadgeSettings.borderWidth}px`,
              borderStyle: 'solid',
              borderColor: `${resolutionBadgeSettings.borderColor}${Math.round(resolutionBadgeSettings.borderOpacity * 255).toString(16)}`,
              boxShadow: resolutionBadgeSettings.shadowEnabled 
                ? `${resolutionBadgeSettings.shadowOffsetX}px ${resolutionBadgeSettings.shadowOffsetY}px ${resolutionBadgeSettings.shadowBlur}px ${resolutionBadgeSettings.shadowColor}` 
                : 'none',
              zIndex: resolutionBadgeSettings.zIndex || 10
            }}
          >
            {resolutionBadgeSettings.resolutionType}
          </div>
        )}
        
        {/* Audio Badge */}
        {displaySettings.showAudioBadge && audioBadgeSettings && (
          <div
            className="absolute bg-black bg-opacity-80 text-white px-2 py-1 rounded"
            style={{
              ...getBadgePositionStyles(audioBadgeSettings.position, audioBadgeSettings.margin),
              fontSize: `${audioBadgeSettings.size / 10}rem`,
              backgroundColor: `${audioBadgeSettings.backgroundColor}${Math.round(audioBadgeSettings.backgroundOpacity * 255).toString(16)}`,
              borderRadius: `${audioBadgeSettings.borderRadius}px`,
              borderWidth: `${audioBadgeSettings.borderWidth}px`,
              borderStyle: 'solid',
              borderColor: `${audioBadgeSettings.borderColor}${Math.round(audioBadgeSettings.borderOpacity * 255).toString(16)}`,
              boxShadow: audioBadgeSettings.shadowEnabled 
                ? `${audioBadgeSettings.shadowOffsetX}px ${audioBadgeSettings.shadowOffsetY}px ${audioBadgeSettings.shadowBlur}px ${audioBadgeSettings.shadowColor}` 
                : 'none',
              zIndex: audioBadgeSettings.zIndex || 10
            }}
          >
            {audioBadgeSettings.codecType}
          </div>
        )}
        
        {/* Review Badge */}
        {displaySettings.showReviewBadge && reviewBadgeSettings && (
          <div
            className="absolute bg-black bg-opacity-80 text-white px-2 py-1 rounded"
            style={{
              ...getBadgePositionStyles(reviewBadgeSettings.position, reviewBadgeSettings.margin),
              fontSize: `${reviewBadgeSettings.size / 10}rem`,
              backgroundColor: `${reviewBadgeSettings.backgroundColor}${Math.round(reviewBadgeSettings.backgroundOpacity * 255).toString(16)}`,
              borderRadius: `${reviewBadgeSettings.borderRadius}px`,
              borderWidth: `${reviewBadgeSettings.borderWidth}px`,
              borderStyle: 'solid',
              borderColor: `${reviewBadgeSettings.borderColor}${Math.round(reviewBadgeSettings.borderOpacity * 255).toString(16)}`,
              boxShadow: reviewBadgeSettings.shadowEnabled 
                ? `${reviewBadgeSettings.shadowOffsetX}px ${reviewBadgeSettings.shadowOffsetY}px ${reviewBadgeSettings.shadowBlur}px ${reviewBadgeSettings.shadowColor}` 
                : 'none',
              zIndex: reviewBadgeSettings.zIndex || 10
            }}
          >
            {reviewBadgeSettings.sources?.slice(0, 2).map((source: any) => `${source.name}: ${source.rating}`).join(' | ')}
          </div>
        )}
      </div>
    </div>
  );
};

export default PosterPreview;