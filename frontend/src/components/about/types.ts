/**
 * TypeScript type definitions for the About page components.
 * Matches the data structures returned by the backend system API endpoints.
 */

export interface SystemInfo {
  version: string;
  execution_mode: string;
  database_schema_hash: string;
  uptime: string;
}

export interface UpdateInfo {
  update_available: boolean;
  current_version: string;
  latest_version?: string;
  message?: string;
  release_notes_url?: string;
}

export interface HealthStatus {
  status: string;
  services: Record<string, string>;
  timestamp: string;
}

export interface SystemStats {
  total_jobs: number;
  successful_jobs: number;
  failed_jobs: number;
  success_rate: number;
  total_media_processed: number;
  database_size: string;
}

export interface LogEntry {
  timestamp: string;
  level: string;
  message: string;
  source: string;
}

export interface AboutPageData {
  systemInfo: SystemInfo;
  updateInfo: UpdateInfo | null;
  healthStatus: HealthStatus;
  stats: SystemStats;
  recentLogs: LogEntry[];
}

export const defaultSystemInfo: SystemInfo = {
  version: 'Unknown',
  execution_mode: 'Unknown',
  database_schema_hash: 'Unknown',
  uptime: 'Unknown'
};

export const defaultHealthStatus: HealthStatus = {
  status: 'unknown',
  services: {},
  timestamp: new Date().toISOString()
};

export const defaultSystemStats: SystemStats = {
  total_jobs: 0,
  successful_jobs: 0,
  failed_jobs: 0,
  success_rate: 0,
  total_media_processed: 0,
  database_size: '0 MB'
};

export const defaultAboutPageData: AboutPageData = {
  systemInfo: defaultSystemInfo,
  updateInfo: null,
  healthStatus: defaultHealthStatus,
  stats: defaultSystemStats,
  recentLogs: []
};

// Link data for the Links section
export interface LinkItem {
  title: string;
  description: string;
  url: string;
  icon: 'website' | 'github';
}

export const defaultLinks: LinkItem[] = [
  {
    title: 'Website',
    description: 'Project homepage',
    url: 'https://github.com/jackkerouac/aphrodite',
    icon: 'website'
  },
  {
    title: 'Source Code',
    description: 'GitHub repository',
    url: 'https://github.com/jackkerouac/aphrodite',
    icon: 'github'
  }
];

// Acknowledgment data for the Acknowledgments section
export interface AcknowledgmentItem {
  title: string;
  description: string;
  author: string;
  authorUrl: string;
  repositoryUrl: string;
}

export const defaultAcknowledgments: AcknowledgmentItem[] = [
  {
    title: 'Kometa',
    description: 'Powerful tool for media library management and metadata enhancement',
    author: 'Kometa Team',
    authorUrl: 'https://github.com/Kometa-Team',
    repositoryUrl: 'https://github.com/Kometa-Team/Kometa'
  },
  {
    title: 'Anime Offline Database',
    description: 'Comprehensive offline anime database for enhanced metadata and functionality',
    author: 'Manami Project',
    authorUrl: 'https://github.com/manami-project',
    repositoryUrl: 'https://github.com/manami-project/anime-offline-database'
  }
];
