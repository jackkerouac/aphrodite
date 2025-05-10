export interface AudioBadgeSettings {
  position: string;
  margin: number;
  background_color: string;
  background_transparency: number;
  border_radius: number;
  border_width: number;
  border_color: string;
  border_transparency: number;
  z_index: number;
  badge_image: string;
  audio_codec_type: string;
  size: number;
}

export interface ResolutionBadgeSettings {
  position: string;
  margin: number;
  background_color: string;
  background_transparency: number;
  border_radius: number;
  border_width: number;
  border_color: string;
  border_transparency: number;
  z_index: number;
  badge_image: string;
  resolution_type: string;
  size: number;
}

export interface ReviewBadgeSettings {
  position: string;
  margin: number;
  background_color: string;
  background_transparency: number;
  border_radius: number;
  border_width: number;
  border_color: string;
  border_transparency: number;
  z_index: number;
  badge_image?: string;
  review_source?: string;
  review_score?: number;
  size?: number;
}