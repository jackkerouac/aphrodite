export interface ReviewSettings {
  General: {
    general_badge_size: number;
    general_edge_padding: number;
    general_badge_position: string;
    general_text_padding: number;
    use_dynamic_sizing: boolean;
    badge_orientation: string;
    badge_spacing: number;
    max_badges_to_display: number;
  };
  Text: {
    font: string;
    fallback_font: string;
    'text-color': string;
    'text-size': number;
  };
  Background: {
    'background-color': string;
    background_opacity: number;
  };
  Border: {
    'border-color': string;
    'border-radius': number;
    border_width: number;
  };
  Shadow: {
    shadow_enable: boolean;
    shadow_blur: number;
    shadow_offset_x: number;
    shadow_offset_y: number;
  };
  ImageBadges: {
    enable_image_badges: boolean;
    codec_image_directory: string;
    fallback_to_text: boolean;
    image_padding: number;
    image_mapping: Record<string, string>;
  };
}

export interface ReviewSource {
  id: number;
  source_name: string;
  enabled: boolean;
  display_order: number;
  priority: number;
  max_variants: number;
  conditions: string | null;
}

export interface ReviewSourceSettings {
  max_badges_display: number;
  source_selection_mode: string;
  show_percentage_only: boolean;
  group_related_sources: boolean;
  anime_sources_for_anime_only: boolean;
}

export const defaultReviewSettings: ReviewSettings = {
  General: {
    general_badge_size: 100,
    general_edge_padding: 30,
    general_badge_position: 'bottom-left',
    general_text_padding: 20,
    use_dynamic_sizing: true,
    badge_orientation: 'vertical',
    badge_spacing: 15,
    max_badges_to_display: 4
  },
  Text: {
    font: 'AvenirNextLTProBold.otf',
    fallback_font: 'DejaVuSans.ttf',
    'text-color': '#FFFFFF',
    'text-size': 60
  },
  Background: {
    'background-color': '#2C2C2C',
    background_opacity: 60
  },
  Border: {
    'border-color': '#2C2C2C',
    'border-radius': 10,
    border_width: 1
  },
  Shadow: {
    shadow_enable: false,
    shadow_blur: 5,
    shadow_offset_x: 2,
    shadow_offset_y: 2
  },
  ImageBadges: {
    enable_image_badges: true,
    codec_image_directory: 'images/rating',
    fallback_to_text: true,
    image_padding: 5,
    image_mapping: {
      'IMDb': 'imdb.png',
      'Rotten Tomatoes': 'rt.png',
      'Metacritic': 'metacritic.png',
      'MyAnimeList': 'mal.png'
    }
  }
};

export const defaultReviewSourceSettings: ReviewSourceSettings = {
  max_badges_display: 4,
  source_selection_mode: 'priority',
  show_percentage_only: true,
  group_related_sources: true,
  anime_sources_for_anime_only: true
};

export const defaultReviewSources: ReviewSource[] = [
  { id: 1, source_name: 'IMDb', enabled: true, display_order: 1, priority: 1, max_variants: 3, conditions: null },
  { id: 2, source_name: 'Rotten Tomatoes Critics', enabled: true, display_order: 2, priority: 2, max_variants: 3, conditions: null },
  { id: 3, source_name: 'Metacritic', enabled: true, display_order: 3, priority: 3, max_variants: 2, conditions: null },
  { id: 4, source_name: 'TMDb', enabled: true, display_order: 4, priority: 4, max_variants: 1, conditions: null },
  { id: 5, source_name: 'AniDB', enabled: true, display_order: 5, priority: 5, max_variants: 1, conditions: '{"content_type": "anime"}' },
  { id: 6, source_name: 'Rotten Tomatoes Audience', enabled: false, display_order: 6, priority: 6, max_variants: 3, conditions: null },
  { id: 7, source_name: 'Letterboxd', enabled: false, display_order: 7, priority: 7, max_variants: 1, conditions: null },
  { id: 8, source_name: 'MyAnimeList', enabled: false, display_order: 8, priority: 8, max_variants: 1, conditions: '{"content_type": "anime"}' },
  { id: 9, source_name: 'Trakt', enabled: false, display_order: 9, priority: 9, max_variants: 1, conditions: null },
  { id: 10, source_name: 'MDBList', enabled: false, display_order: 10, priority: 10, max_variants: 1, conditions: null }
];
