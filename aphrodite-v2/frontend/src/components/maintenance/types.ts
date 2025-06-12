/**
 * TypeScript type definitions for the Maintenance page components.
 * Matches the data structures used by maintenance operations and API endpoints.
 */

// Connection testing types (reusing API Settings logic)
export interface ConnectionStatus {
  success: boolean;
  message: string;
}

export interface ApiConnection {
  name: string;
  description: string;
  status: 'checking' | 'connected' | 'failed' | null;
  error?: string;
}

export interface ConnectionTestData {
  jellyfin: boolean;
  omdb: boolean;
  tmdb: boolean;
  mdblist: boolean;
  anidb: boolean;
  isTestingAll: boolean;
}

// Database operations types
export interface DatabaseInfo {
  database: {
    exists: boolean;
    path: string;
    size: number;
    size_formatted: string;
  };
  schema_version: string;
  backups: BackupFile[];
  backup_directory: string;
}

export interface BackupFile {
  filename: string;
  size: number;
  size_formatted: string;
  created: string;
  compressed: boolean;
}

export interface IntegrityStatus {
  checked: boolean;
  ok: boolean;
  message?: string;
}

export interface BackupOptions {
  compress: boolean;
}

export interface CleanupOptions {
  keepCount: number;
}

export interface ExportOptions {
  includeSensitive: boolean;
}

export interface DatabaseOperationResult {
  success: boolean;
  message: string;
  details?: Record<string, any>;
}

// Logs types
export interface LogEntry {
  line_number: number;
  timestamp: string;
  level: string;
  message: string;
}

export interface LogFileInfo {
  total_lines: number;
  filtered_lines: number;
  file_size: number;
  file_modified: string;
}

export interface LogsData {
  logs: LogEntry[];
  fileInfo: LogFileInfo | null;
  availableLevels: string[];
  selectedLevel: string;
  searchQuery: string;
  isLoading: boolean;
  error: string;
}

// Main maintenance page data structure
export interface MaintenancePageData {
  connectionTests: ConnectionTestData;
  databaseInfo: DatabaseInfo | null;
  integrityStatus: IntegrityStatus;
  backupOptions: BackupOptions;
  cleanupOptions: CleanupOptions;
  exportOptions: ExportOptions;
  logsData: LogsData;
}

// Default values
export const defaultConnectionTestData: ConnectionTestData = {
  jellyfin: false,
  omdb: false,
  tmdb: false,
  mdblist: false,
  anidb: false,
  isTestingAll: false
};

export const defaultIntegrityStatus: IntegrityStatus = {
  checked: false,
  ok: false
};

export const defaultBackupOptions: BackupOptions = {
  compress: true
};

export const defaultCleanupOptions: CleanupOptions = {
  keepCount: 5
};

export const defaultExportOptions: ExportOptions = {
  includeSensitive: false
};

export const defaultLogsData: LogsData = {
  logs: [],
  fileInfo: null,
  availableLevels: [],
  selectedLevel: '',
  searchQuery: '',
  isLoading: false,
  error: ''
};

export const defaultMaintenancePageData: MaintenancePageData = {
  connectionTests: defaultConnectionTestData,
  databaseInfo: null,
  integrityStatus: defaultIntegrityStatus,
  backupOptions: defaultBackupOptions,
  cleanupOptions: defaultCleanupOptions,
  exportOptions: defaultExportOptions,
  logsData: defaultLogsData
};

// Service definitions for connection testing
export const apiServices: ApiConnection[] = [
  {
    name: 'Jellyfin',
    description: 'Check connection to Jellyfin server using configured API key',
    status: null
  },
  {
    name: 'OMDB',
    description: 'Check connection to OMDB API using configured API key',
    status: null
  },
  {
    name: 'TMDB',
    description: 'Check connection to TMDB API using configured API key',
    status: null
  },
  {
    name: 'MDBList',
    description: 'Check connection to MDBList API using configured API key',
    status: null
  },
  {
    name: 'AniDB',
    description: 'Check connection to AniDB using configured credentials',
    status: null
  }
];
