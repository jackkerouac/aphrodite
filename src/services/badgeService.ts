import { apiClient } from '@/lib/apiClient';

// Field mappings for compatibility with backend
const mapAudioBadgeToBackend = (settings: AudioBadgeSettings): any => {
  return {
    size: settings.size,
    margin: settings.margin,
    position: settings.position,
    codec_type: settings.codecType,
    background_color: settings.backgroundColor,
    background_opacity: settings.backgroundOpacity,
    border_radius: settings.borderRadius,
    border_width: settings.borderWidth,
    border_color: settings.borderColor,
    border_opacity: settings.borderOpacity,
    shadow_enabled: settings.shadowEnabled,
    shadow_color: settings.shadowColor,
    shadow_blur: settings.shadowBlur,
    shadow_offset_x: settings.shadowOffsetX,
    shadow_offset_y: settings.shadowOffsetY,
    z_index: settings.zIndex || 1,
    badge_image: settings.badgeImage,
    enabled: settings.enabled
  };
};

const mapBackendToAudioBadge = (data: any): AudioBadgeSettings => {
  return {
    size: data.size,
    margin: data.margin,
    position: data.position,
    codecType: data.codec_type,
    backgroundColor: data.background_color,
    backgroundOpacity: data.background_opacity,
    borderRadius: data.border_radius,
    borderWidth: data.border_width,
    borderColor: data.border_color,
    borderOpacity: data.border_opacity,
    shadowEnabled: data.shadow_enabled,
    shadowColor: data.shadow_color,
    shadowBlur: data.shadow_blur,
    shadowOffsetX: data.shadow_offset_x,
    shadowOffsetY: data.shadow_offset_y,
    zIndex: data.z_index || 1,
    badgeImage: data.badge_image,
    enabled: data.enabled !== false
  };
};

const mapResolutionBadgeToBackend = (settings: ResolutionBadgeSettings): any => {
  return {
    size: settings.size,
    margin: settings.margin,
    position: settings.position,
    resolution_type: settings.resolutionType,
    background_color: settings.backgroundColor,
    background_opacity: settings.backgroundOpacity,
    border_radius: settings.borderRadius,
    border_width: settings.borderWidth,
    border_color: settings.borderColor,
    border_opacity: settings.borderOpacity,
    shadow_enabled: settings.shadowEnabled,
    shadow_color: settings.shadowColor,
    shadow_blur: settings.shadowBlur,
    shadow_offset_x: settings.shadowOffsetX,
    shadow_offset_y: settings.shadowOffsetY,
    z_index: settings.zIndex || 2,
    use_custom_text: settings.useCustomText,
    custom_text: settings.customText,
    direct_image_render: settings.directImageRender,
    enabled: settings.enabled
  };
};

const mapBackendToResolutionBadge = (data: any): ResolutionBadgeSettings => {
  return {
    size: data.size,
    margin: data.margin,
    position: data.position,
    resolutionType: data.resolution_type,
    backgroundColor: data.background_color,
    backgroundOpacity: data.background_opacity,
    borderRadius: data.border_radius,
    borderWidth: data.border_width,
    borderColor: data.border_color,
    borderOpacity: data.border_opacity,
    shadowEnabled: data.shadow_enabled,
    shadowColor: data.shadow_color,
    shadowBlur: data.shadow_blur,
    shadowOffsetX: data.shadow_offset_x,
    shadowOffsetY: data.shadow_offset_y,
    zIndex: data.z_index || 2,
    useCustomText: data.use_custom_text,
    customText: data.custom_text,
    directImageRender: data.direct_image_render,
    enabled: data.enabled !== false
  };
};

const mapReviewBadgeToBackend = (settings: ReviewBadgeSettings): any => {
  return {
    size: settings.size,
    margin: settings.margin,
    position: settings.position,
    background_color: settings.backgroundColor,
    background_opacity: settings.backgroundOpacity,
    border_radius: settings.borderRadius,
    border_width: settings.borderWidth,
    border_color: settings.borderColor,
    border_opacity: settings.borderOpacity,
    shadow_enabled: settings.shadowEnabled,
    shadow_color: settings.shadowColor,
    shadow_blur: settings.shadowBlur,
    shadow_offset_x: settings.shadowOffsetX,
    shadow_offset_y: settings.shadowOffsetY,
    z_index: settings.zIndex || 3,
    badge_layout: settings.displayFormat,
    show_logo: settings.showIcons,
    logo_size: settings.logoSize,
    logo_position: settings.logoPosition,
    logo_text_spacing: settings.logoTextSpacing,
    spacing: settings.spacing,
    font_family: settings.fontFamily,
    font_size: settings.fontSize,
    font_weight: settings.fontWeight,
    text_color: settings.textColor,
    text_opacity: settings.textOpacity,
    display_sources: settings.displaySources,
    source_order: settings.sourceOrder,
    score_format: settings.scoreFormat,
    enabled: settings.enabled
  };
};

const mapBackendToReviewBadge = (data: any): ReviewBadgeSettings => {
  return {
    type: 'review',
    size: data.size,
    margin: data.margin,
    position: data.position,
    backgroundColor: data.background_color,
    backgroundOpacity: data.background_opacity,
    borderRadius: data.border_radius,
    borderWidth: data.border_width,
    borderColor: data.border_color,
    borderOpacity: data.border_opacity,
    shadowEnabled: data.shadow_enabled,
    shadowColor: data.shadow_color,
    shadowBlur: data.shadow_blur,
    shadowOffsetX: data.shadow_offset_x,
    shadowOffsetY: data.shadow_offset_y,
    zIndex: data.z_index || 3,
    displayFormat: data.badge_layout,
    showIcons: data.show_logo,
    logoSize: data.logo_size,
    logoPosition: data.logo_position,
    logoTextSpacing: data.logo_text_spacing,
    spacing: data.spacing,
    fontFamily: data.font_family,
    fontSize: data.font_size,
    fontWeight: data.font_weight,
    textColor: data.text_color,
    textOpacity: data.text_opacity,
    displaySources: data.display_sources,
    sourceOrder: data.source_order,
    scoreFormat: data.score_format,
    enabled: data.enabled !== false
  };
};

// Audio Badge Settings
export interface AudioBadgeSettings {
  id?: number;
  user_id: string;
  size: number;
  margin: number;
  position: string;
  audio_codec_type?: string;
  background_color: string;
  background_transparency?: number;
  border_radius: number;
  border_width: number;
  border_color: string;
  border_transparency?: number;
  shadow_toggle?: boolean;
  shadow_color?: string;
  shadow_blur_radius?: number;
  shadow_offset_x?: number;
  shadow_offset_y?: number;
  z_index: number;
  badge_image?: string;
  enabled?: boolean;
}

// Resolution Badge Settings
export interface ResolutionBadgeSettings {
  id?: number;
  user_id: string;
  size: number;
  margin: number;
  position: string;
  resolution_type?: string;
  background_color: string;
  background_transparency?: number;
  border_radius: number;
  border_width: number;
  border_color: string;
  border_transparency?: number;
  shadow_toggle?: boolean;
  shadow_color?: string;
  shadow_blur_radius?: number;
  shadow_offset_x?: number;
  shadow_offset_y?: number;
  z_index: number;
  direct_image_render?: boolean;
  use_custom_text?: boolean;
  custom_text?: string;
  enabled?: boolean;
}

// Review Badge Settings
export interface ReviewBadgeSettings {
  id?: number;
  user_id: string;
  size: number;
  margin: number;
  background_color: string;
  background_transparency?: number;
  border_radius: number;
  border_width: number;
  border_color: string;
  border_transparency?: number;
  shadow_toggle?: boolean;
  shadow_color?: string;
  shadow_blur_radius?: number;
  shadow_offset_x?: number;
  shadow_offset_y?: number;
  z_index: number;
  position: string;
  badge_layout?: string;
  display_sources?: string[];
  source_order?: string[];
  show_logo?: boolean;
  logo_size?: number;
  logo_position?: string;
  logo_text_spacing?: number;
  score_format?: string;
  spacing?: number;
  font_family?: string;
  font_size?: number;
  font_weight?: number;
  text_color?: string;
  text_transparency?: number;
  enabled?: boolean;
}

// Audio Badge API Functions
export const fetchAudioBadgeSettings = async (userId: string): Promise<AudioBadgeSettings | null> => {
  try {
    const data = await apiClient.get(`audio-badge-settings/${userId}`);
    return data ? mapBackendToAudioBadge(data) : null;
  } catch (error) {
    console.error('Error fetching audio badge settings:', error);
    return null;
  }
};

export const updateAudioBadgeSettings = async (userId: string, settings: AudioBadgeSettings): Promise<AudioBadgeSettings | null> => {
  try {
    const backendSettings = mapAudioBadgeToBackend(settings);
    const data = await apiClient.post(`audio-badge-settings/${userId}`, backendSettings);
    return data ? mapBackendToAudioBadge(data) : null;
  } catch (error) {
    console.error('Error updating audio badge settings:', error);
    return null;
  }
};

// Resolution Badge API Functions
export const fetchResolutionBadgeSettings = async (userId: string): Promise<ResolutionBadgeSettings | null> => {
  try {
    const data = await apiClient.get(`resolution-badge-settings/${userId}`);
    return data ? mapBackendToResolutionBadge(data) : null;
  } catch (error) {
    console.error('Error fetching resolution badge settings:', error);
    return null;
  }
};

export const updateResolutionBadgeSettings = async (userId: string, settings: ResolutionBadgeSettings): Promise<ResolutionBadgeSettings | null> => {
  try {
    const backendSettings = mapResolutionBadgeToBackend(settings);
    const data = await apiClient.post(`resolution-badge-settings/${userId}`, backendSettings);
    return data ? mapBackendToResolutionBadge(data) : null;
  } catch (error) {
    console.error('Error updating resolution badge settings:', error);
    return null;
  }
};

// Review Badge API Functions
export const fetchReviewBadgeSettings = async (userId: string): Promise<ReviewBadgeSettings | null> => {
  try {
    const data = await apiClient.get(`review-badge-settings/${userId}`);
    return data ? mapBackendToReviewBadge(data) : null;
  } catch (error) {
    console.error('Error fetching review badge settings:', error);
    return null;
  }
};

export const updateReviewBadgeSettings = async (userId: string, settings: ReviewBadgeSettings): Promise<ReviewBadgeSettings | null> => {
  try {
    const backendSettings = mapReviewBadgeToBackend(settings);
    const data = await apiClient.post(`review-badge-settings/${userId}`, backendSettings);
    return data ? mapBackendToReviewBadge(data) : null;
  } catch (error) {
    console.error('Error updating review badge settings:', error);
    return null;
  }
};
