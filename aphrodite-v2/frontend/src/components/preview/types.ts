/**
 * TypeScript type definitions for the Preview page components.
 * Matches the data structures used by preview operations and API endpoints.
 */

// Badge type definitions
export interface BadgeType {
  id: string;
  name: string;
  description: string;
}

// Preview request/response types
export interface PreviewRequest {
  badgeTypes: string[];
}

export interface PreviewJob {
  id: string;
  status: 'queued' | 'running' | 'success' | 'failed';
  message?: string;
  result?: {
    success: boolean;
    poster_url?: string;
    badges_applied?: string[];
    source_poster?: string;
    error?: string;
  };
}

// Library browser types (for future Jellyfin integration)
export interface JellyfinLibrary {
  id: string;
  name: string;
  type: 'movies' | 'series' | 'music' | 'books';
  itemCount?: number;
}

export interface MediaItem {
  id: string;
  name: string;
  type: 'movie' | 'series' | 'episode' | 'season';
  year?: number;
  poster_url?: string;
  overview?: string;
}

export interface MediaSearchParams {
  library_id?: string;
  search?: string;
  page?: number;
  limit?: number;
}

// Preview configuration types
export interface PreviewConfiguration {
  selectedBadgeTypes: string[];
  selectedLibrary?: string;
  selectedMedia?: string;
  previewOptions: {
    useExamplePoster: boolean;
    overlayOpacity: number;
    showBeforeAfter: boolean;
  };
}

// Processing control types
export interface ProcessingJob {
  id: string;
  type: 'preview' | 'apply' | 'batch';
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: number;
  media_ids: string[];
  badge_types: string[];
  created_at: string;
  updated_at: string;
  result?: any;
}

export interface ProcessingQueue {
  jobs: ProcessingJob[];
  activeJobs: number;
  maxConcurrent: number;
  totalCompleted: number;
  totalFailed: number;
}

// Main preview page data structure
export interface PreviewPageData {
  // Badge types and selection
  availableBadgeTypes: BadgeType[];
  selectedBadgeTypes: string[];
  
  // Current preview
  currentPreview: {
    isGenerating: boolean;
    jobId?: string;
    previewUrl?: string;
    sourcePoster?: string;
    error?: string;
  };
  
  // Library browser (future feature)
  libraries: JellyfinLibrary[];
  selectedLibrary?: string;
  mediaItems: MediaItem[];
  selectedMedia?: string;
  
  // Configuration
  configuration: PreviewConfiguration;
  
  // Processing queue
  processingQueue: ProcessingQueue;
  
  // UI state
  isLoading: boolean;
  activeTab: 'simple' | 'advanced';
}

// Default values following the maintenance pattern
export const defaultBadgeTypes: BadgeType[] = [
  {
    id: 'audio',
    name: 'Audio',
    description: 'Audio codec badges (DTS-X, Atmos, etc.)'
  },
  {
    id: 'resolution',
    name: 'Resolution',
    description: 'Resolution badges (4K, 1080p, etc.)'
  },
  {
    id: 'review',
    name: 'Review',
    description: 'Review/rating badges (IMDb, TMDb, etc.)'
  },
  {
    id: 'awards',
    name: 'Awards',
    description: 'Awards badges (Oscars, Emmys, etc.)'
  }
];

export const defaultPreviewConfiguration: PreviewConfiguration = {
  selectedBadgeTypes: ['audio', 'resolution'],
  previewOptions: {
    useExamplePoster: true,
    overlayOpacity: 0.8,
    showBeforeAfter: true
  }
};

export const defaultProcessingQueue: ProcessingQueue = {
  jobs: [],
  activeJobs: 0,
  maxConcurrent: 3,
  totalCompleted: 0,
  totalFailed: 0
};

export const defaultPreviewPageData: PreviewPageData = {
  availableBadgeTypes: defaultBadgeTypes,
  selectedBadgeTypes: ['audio', 'resolution'],
  currentPreview: {
    isGenerating: false
  },
  libraries: [],
  mediaItems: [],
  configuration: defaultPreviewConfiguration,
  processingQueue: defaultProcessingQueue,
  isLoading: false,
  activeTab: 'simple'
};

// API response types
export interface BadgeTypesResponse {
  success: boolean;
  badgeTypes: BadgeType[];
}

export interface PreviewResponse {
  success: boolean;
  message: string;
  jobId: string;
}

export interface LibrariesResponse {
  success: boolean;
  libraries: JellyfinLibrary[];
}

export interface MediaResponse {
  success: boolean;
  media: MediaItem[];
  total: number;
  page: number;
  limit: number;
}

export interface JobStatusResponse {
  success: boolean;
  job: PreviewJob;
}
