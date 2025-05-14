/**
 * Types for unified badge settings system
 */

// Badge position options
export enum BadgePosition {
  TopLeft = 'top-left',
  TopCenter = 'top-center',
  TopRight = 'top-right',
  MiddleLeft = 'middle-left',
  Center = 'center',
  MiddleRight = 'middle-right',
  BottomLeft = 'bottom-left',
  BottomCenter = 'bottom-center',
  BottomRight = 'bottom-right'
}

// Review badge display format
export enum DisplayFormat {
  Horizontal = 'horizontal',
  Vertical = 'vertical'
}

// Base badge settings interface with common properties
export interface BaseBadgeSettings {
  id?: number;
  user_id: number | string;
  badge_type: string;
  
  // General Settings
  badge_size: number; // 1-500
  edge_padding: number; // 1-50
  badge_position: BadgePosition;
  
  // Background Settings
  background_color: string;
  background_opacity: number; // 0-100
  
  // Border Settings
  border_size: number; // 0-10
  border_color: string;
  border_opacity: number; // 0-100
  border_radius: number; // 0-50
  border_width: number; // 0-10
  
  // Shadow Settings
  shadow_enabled: boolean;
  shadow_color: string;
  shadow_blur: number; // 0-20
  shadow_offset_x: number; // -20 to 20
  shadow_offset_y: number; // -20 to 20
  
  // Timestamps
  created_at?: string;
  updated_at?: string;
}

// Audio badge specific properties
export interface AudioBadgeProperties {
  codec_type: string; // e.g., 'dolby_atmos', 'dts', etc.
}

// Resolution badge specific properties
export interface ResolutionBadgeProperties {
  resolution_type: string; // e.g., '4k', '1080p', etc.
}

// Review badge specific properties
export interface ReviewBadgeProperties {
  review_sources: string[]; // e.g., ['imdb', 'rotten_tomatoes']
  score_type?: string; // e.g., 'percentage', 'rating'
}

// Audio badge settings
export interface AudioBadgeSettings extends BaseBadgeSettings {
  badge_type: 'audio';
  properties: AudioBadgeProperties;
}

// Resolution badge settings
export interface ResolutionBadgeSettings extends BaseBadgeSettings {
  badge_type: 'resolution';
  properties: ResolutionBadgeProperties;
}

// Review badge settings
export interface ReviewBadgeSettings extends BaseBadgeSettings {
  badge_type: 'review';
  display_format: DisplayFormat;
  properties: ReviewBadgeProperties;
}

// Union type for all badge settings
export type UnifiedBadgeSettings = AudioBadgeSettings | ResolutionBadgeSettings | ReviewBadgeSettings;

// Default values for new badge settings
export const DEFAULT_AUDIO_BADGE_SETTINGS: AudioBadgeSettings = {
  user_id: '1',
  badge_type: 'audio',
  badge_size: 200, // Match the size in the database (200 instead of 100)
  edge_padding: 30, // Match padding in database
  badge_position: BadgePosition.TopLeft,
  background_color: '#05ed2e', // Green color used in preview
  background_opacity: 80,
  border_size: 2,
  border_color: '#FFFFFF',
  border_opacity: 80,
  border_radius: 10,
  border_width: 1,
  shadow_enabled: true,
  shadow_color: '#000000',
  shadow_blur: 8,
  shadow_offset_x: 2,
  shadow_offset_y: 2,
  properties: {
    codec_type: 'dolby_atmos'
  }
};

export const DEFAULT_RESOLUTION_BADGE_SETTINGS: ResolutionBadgeSettings = {
  user_id: '1',
  badge_type: 'resolution',
  badge_size: 194, // Match the size in the database (194 instead of 100)
  edge_padding: 30, // Match padding in database
  badge_position: BadgePosition.TopRight,
  background_color: '#e220e8', // Purple color used in preview
  background_opacity: 80,
  border_size: 2,
  border_color: '#FFFFFF',
  border_opacity: 80,
  border_radius: 10,
  border_width: 1,
  shadow_enabled: true,
  shadow_color: '#000000',
  shadow_blur: 8,
  shadow_offset_x: 2,
  shadow_offset_y: 2,
  properties: {
    resolution_type: '4k'
  }
};

export const DEFAULT_REVIEW_BADGE_SETTINGS: ReviewBadgeSettings = {
  user_id: '1',
  badge_type: 'review',
  badge_size: 231, // Match the size in the database (231 instead of 100)
  edge_padding: 30, // Match padding in database
  badge_position: BadgePosition.BottomLeft,
  display_format: DisplayFormat.Vertical, // Vertical looks better than horizontal
  background_color: '#d12125', // Red color used in preview
  background_opacity: 48, // Lower opacity for review badges
  border_size: 2,
  border_color: '#d12125', // Border matches background
  border_opacity: 80,
  border_radius: 13, // Larger radius for review badges
  border_width: 1,
  shadow_enabled: false,
  shadow_color: '#000000',
  shadow_blur: 10,
  shadow_offset_x: 0,
  shadow_offset_y: 0,
  properties: {
    review_sources: ['imdb', 'tmdb', 'rt_critic'], // Match sources in database
    score_type: 'percentage'
  }
};
