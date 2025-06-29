export interface ResolutionSettings {
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
  enhanced_detection: {
    enabled: boolean;
    fallback_rules: Record<string, string>;
    hdr_detection_patterns: string[];
    dv_detection_patterns: string[];
    priority_order: string[];
  };
  performance: {
    enable_parallel_processing: boolean;
    enable_caching: boolean;
    cache_ttl_hours: number;
    max_episodes_to_sample: number;
  };
}

export interface ImageCoverageReport {
  total_images: number;
  coverage_by_resolution: Record<string, {
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
}

export interface CacheStats {
  hit_rate_percent: number;
  total_hits: number;
  total_misses: number;
  cache_size: number;
  ttl_hours: number;
  last_cleanup: string;
}

export interface DiagnosticResults {
  imageCoverage?: ImageCoverageReport;
  cacheStats?: CacheStats;
  testResults?: {
    test_passed: boolean;
    detected_resolution: string;
    used_image: string;
    detection_method: string;
    processing_time_ms: number;
  };
}

export const defaultResolutionSettings: ResolutionSettings = {
  General: {
    general_badge_size: 100,
    general_edge_padding: 30,
    general_badge_position: 'top-right',
    general_text_padding: 12,
    use_dynamic_sizing: true
  },
  Text: {
    font: 'AvenirNextLTProBold.otf',
    fallback_font: 'DejaVuSans.ttf',
    'text-color': '#FFFFFF',
    'text-size': 90
  },
  Background: {
    'background-color': '#000000',
    background_opacity: 40
  },
  Border: {
    'border-color': '#000000',
    'border-radius': 10,
    border_width: 1
  },
  Shadow: {
    shadow_enable: false,
    shadow_blur: 8,
    shadow_offset_x: 2,
    shadow_offset_y: 2
  },
  ImageBadges: {
    enable_image_badges: true,
    codec_image_directory: 'images/resolution',
    fallback_to_text: true,
    image_padding: 20,
    image_mapping: {
      '4K': '4K.png',
      '1080p': '1080p.png',
      '720p': '720p.png',
      '480p': '480p.png',
      'SD': 'SD.png'
    }
  },
  enhanced_detection: {
    enabled: false,
    fallback_rules: {
      '1440p': '1080p',
      '8k': '4k',
      '2160p': '4k'
    },
    hdr_detection_patterns: [
      'HDR',
      'HDR10',
      'BT2020',
      'PQ',
      'ST2084',
      'HLG'
    ],
    dv_detection_patterns: [
      'DV',
      'DOLBY VISION',
      'DVHE',
      'DVH1'
    ],
    priority_order: [
      'dvhdrplus',
      'dvhdr',
      'dvplus',
      'hdrplus',
      'dv',
      'hdr',
      'plus',
      'base'
    ]
  },
  performance: {
    enable_parallel_processing: true,
    enable_caching: true,
    cache_ttl_hours: 24,
    max_episodes_to_sample: 5
  }
};
