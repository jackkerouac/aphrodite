export interface AudioSettings {
  General: {
    general_badge_size: number;
    general_edge_padding: number;
    general_badge_position: string;
    general_text_padding: number;
    use_dynamic_sizing: boolean;
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
  EnhancedDetection: {
    enabled: boolean;
    fallback_rules: Record<string, string>;
    atmos_detection_patterns: string[];
    dts_x_detection_patterns: string[];
    priority_order: string[];
  };
  Performance: {
    enable_parallel_processing: boolean;
    enable_caching: boolean;
    cache_ttl_hours: number;
    max_episodes_to_sample: number;
  };
}

export interface AudioCoverageReport {
  total_images: number;
  coverage_by_audio_format: Record<string, {
    available_variants: string[];
    missing_variants: string[];
    has_base: boolean;
  }>;
  missing_combinations: string[];
  standalone_images: string[];
  fallback_coverage: Record<string, {
    target: string;
    target_available: boolean;
  }>;
  atmos_images: string[];
  dts_x_images: string[];
}

export interface AudioCacheStats {
  hit_rate_percent: number;
  total_hits: number;
  total_misses: number;
  cache_size: number;
  ttl_hours: number;
  last_cleanup: string;
  episode_samples_cached: number;
}

export interface AudioDetectionTestResult {
  test_passed: boolean;
  detected_audio: string;
  used_image: string;
  detection_method: string;
  processing_time_ms: number;
  atmos_detected: boolean;
  dts_x_detected: boolean;
}
