import { AudioBadgeSettings } from '@/components/badges/types/AudioBadge';
import { ResolutionBadgeSettings } from '@/components/badges/types/ResolutionBadge';
import { ReviewBadgeSettings } from '@/components/badges/types/ReviewBadge';

// Import individual badge renderers
import { renderAudioBadge } from './badges/audioBadge';
import { renderResolutionBadge } from './badges/resolutionBadge';
import { renderReviewBadge } from './badges/reviewBadge';

// Export utility functions
export { extractBadgeWithTransparency } from './badges/utils';

export type BadgeType = 'audio' | 'resolution' | 'review';

export interface BadgeRenderingCommonOptions {
  position?: {
    percentX: number;
    percentY: number;
  };
}

export interface BadgeRenderingResult {
  canvas: HTMLCanvasElement;
  position?: {
    percentX: number;
    percentY: number;
  };
}

/**
 * Renders a badge to a canvas based on the badge type and options
 * @param type The type of badge to render
 * @param options The options for rendering the badge
 * @param sourceImageUrl Optional image URL to use as badge source
 * @returns Promise resolving to a canvas element with the rendered badge
 */
export const renderBadgeToCanvas = async (
  type: BadgeType,
  options: AudioBadgeSettings | ResolutionBadgeSettings | ReviewBadgeSettings & BadgeRenderingCommonOptions,
  sourceImageUrl?: string
): Promise<BadgeRenderingResult> => {
  const position = options.position || { percentX: 0, percentY: 0 };
  let canvas: HTMLCanvasElement;
  
  // Debug: Log the options being passed in
  console.log(`renderBadgeToCanvas called for type ${type}`);
  
  switch (type) {
    case 'audio': {
      const audioOptions = options as AudioBadgeSettings;
      canvas = await renderAudioBadge(audioOptions, sourceImageUrl);
      break;
    }
    case 'resolution': {
      const resolutionOptions = options as ResolutionBadgeSettings;
      canvas = await renderResolutionBadge(resolutionOptions, sourceImageUrl);
      break;
    }
    case 'review': {
      const reviewOptions = options as ReviewBadgeSettings;
      canvas = await renderReviewBadge(reviewOptions, sourceImageUrl);
      break;
    }
    default:
      throw new Error(`Unsupported badge type: ${type}`);
  }

  return {
    canvas,
    position
  };
};