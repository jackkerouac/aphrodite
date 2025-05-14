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

// REMOVED: No more default settings - force the system to always use database values
