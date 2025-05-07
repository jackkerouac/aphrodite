import React from 'react';
import { BadgeDisplaySettings } from '../hooks/useBadgePreviewSettings';

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
        
        {/* Resolution Badge Placeholder */}
        {displaySettings.showResolutionBadge && resolutionBadgeSettings && (
          <div
            className="absolute bg-black bg-opacity-80 text-white px-2 py-1 rounded"
            style={{
              top: resolutionBadgeSettings.position.includes('top') ? `${resolutionBadgeSettings.margin}px` : 'auto',
              bottom: resolutionBadgeSettings.position.includes('bottom') ? `${resolutionBadgeSettings.margin}px` : 'auto',
              left: resolutionBadgeSettings.position.includes('left') ? `${resolutionBadgeSettings.margin}px` : 'auto',
              right: resolutionBadgeSettings.position.includes('right') ? `${resolutionBadgeSettings.margin}px` : 'auto',
              fontSize: `${resolutionBadgeSettings.size / 10}rem`,
              backgroundColor: `${resolutionBadgeSettings.background_color}${Math.round(resolutionBadgeSettings.background_transparency * 255).toString(16)}`,
              borderRadius: `${resolutionBadgeSettings.border_radius}px`,
              borderWidth: `${resolutionBadgeSettings.border_width}px`,
              borderStyle: 'solid',
              borderColor: `${resolutionBadgeSettings.border_color}${Math.round(resolutionBadgeSettings.border_transparency * 255).toString(16)}`,
              boxShadow: resolutionBadgeSettings.shadow_toggle 
                ? `${resolutionBadgeSettings.shadow_offset_x}px ${resolutionBadgeSettings.shadow_offset_y}px ${resolutionBadgeSettings.shadow_blur_radius}px ${resolutionBadgeSettings.shadow_color}` 
                : 'none',
              zIndex: resolutionBadgeSettings.z_index
            }}
          >
            {resolutionBadgeSettings.resolution_type}
          </div>
        )}
        
        {/* Audio Badge Placeholder */}
        {displaySettings.showAudioBadge && audioBadgeSettings && (
          <div
            className="absolute bg-black bg-opacity-80 text-white px-2 py-1 rounded"
            style={{
              top: audioBadgeSettings.position.includes('top') ? `${audioBadgeSettings.margin}px` : 'auto',
              bottom: audioBadgeSettings.position.includes('bottom') ? `${audioBadgeSettings.margin}px` : 'auto',
              left: audioBadgeSettings.position.includes('left') ? `${audioBadgeSettings.margin}px` : 'auto',
              right: audioBadgeSettings.position.includes('right') ? `${audioBadgeSettings.margin}px` : 'auto',
              fontSize: `${audioBadgeSettings.size / 10}rem`,
              backgroundColor: `${audioBadgeSettings.background_color}${Math.round(audioBadgeSettings.background_transparency * 255).toString(16)}`,
              borderRadius: `${audioBadgeSettings.border_radius}px`,
              borderWidth: `${audioBadgeSettings.border_width}px`,
              borderStyle: 'solid',
              borderColor: `${audioBadgeSettings.border_color}${Math.round(audioBadgeSettings.border_transparency * 255).toString(16)}`,
              boxShadow: audioBadgeSettings.shadow_toggle 
                ? `${audioBadgeSettings.shadow_offset_x}px ${audioBadgeSettings.shadow_offset_y}px ${audioBadgeSettings.shadow_blur_radius}px ${audioBadgeSettings.shadow_color}` 
                : 'none',
              zIndex: audioBadgeSettings.z_index
            }}
          >
            {audioBadgeSettings.audio_codec_type}
          </div>
        )}
        
        {/* Review Badge Placeholder */}
        {displaySettings.showReviewBadge && reviewBadgeSettings && (
          <div
            className="absolute bg-black bg-opacity-80 text-white px-2 py-1 rounded"
            style={{
              top: reviewBadgeSettings.position.includes('top') ? `${reviewBadgeSettings.margin}px` : 'auto',
              bottom: reviewBadgeSettings.position.includes('bottom') ? `${reviewBadgeSettings.margin}px` : 'auto',
              left: reviewBadgeSettings.position.includes('left') ? `${reviewBadgeSettings.margin}px` : 'auto',
              right: reviewBadgeSettings.position.includes('right') ? `${reviewBadgeSettings.margin}px` : 'auto',
              fontSize: `${reviewBadgeSettings.size / 10}rem`,
              backgroundColor: `${reviewBadgeSettings.background_color}${Math.round(reviewBadgeSettings.background_transparency * 255).toString(16)}`,
              borderRadius: `${reviewBadgeSettings.border_radius}px`,
              borderWidth: `${reviewBadgeSettings.border_width}px`,
              borderStyle: 'solid',
              borderColor: `${reviewBadgeSettings.border_color}${Math.round(reviewBadgeSettings.border_transparency * 255).toString(16)}`,
              boxShadow: reviewBadgeSettings.shadow_toggle 
                ? `${reviewBadgeSettings.shadow_offset_x}px ${reviewBadgeSettings.shadow_offset_y}px ${reviewBadgeSettings.shadow_blur_radius}px ${reviewBadgeSettings.shadow_color}` 
                : 'none',
              zIndex: reviewBadgeSettings.z_index
            }}
          >
            {reviewBadgeSettings.display_sources?.slice(0, 2).map((source: string) => `${source}: 8.5`).join(' | ')}
          </div>
        )}
      </div>
    </div>
  );
};

export default PosterPreview;
