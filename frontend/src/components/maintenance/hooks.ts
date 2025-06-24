import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import { 
  MaintenancePageData, 
  defaultMaintenancePageData,
  ConnectionStatus,
  ApiConnection,
  apiServices,
  DatabaseInfo,
  DatabaseOperationResult,
  LogEntry,
  LogFileInfo
} from './types';

export function useMaintenanceData() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<MaintenancePageData>(defaultMaintenancePageData);

  // Load initial maintenance data
  const loadMaintenanceData = async () => {
    setLoading(true);
    
    try {
      console.log('Loading maintenance page data...');
      
      // Load database info and logs data in parallel
      const [databaseResponse, logsLevelsResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/database/status`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/logs/levels`)
      ]);

      const databaseData = await databaseResponse.json();
      const logsLevelsData = await logsLevelsResponse.json();

      console.log('Loaded maintenance data:', { databaseData, logsLevelsData });

      // Update state with loaded data
      setData(prev => ({
        ...prev,
        databaseInfo: databaseData.success ? databaseData : null,
        logsData: {
          ...prev.logsData,
          availableLevels: logsLevelsData.success ? logsLevelsData.levels : []
        }
      }));

      console.log('Maintenance page data loaded successfully');
    } catch (error) {
      console.error('Error loading maintenance page data:', error);
      toast.error('Failed to load maintenance information', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  // Refresh data
  const refreshData = async () => {
    await loadMaintenanceData();
  };

  return {
    loading,
    data,
    loadMaintenanceData,
    refreshData,
    setData
  };
}

// Connection testing hook (reusing API Settings logic)
export function useConnectionTesting() {
  const [services, setServices] = useState<ApiConnection[]>(apiServices.map(s => ({ ...s })));
  const [isTestingAll, setIsTestingAll] = useState(false);

  // Test individual connection
  const testConnection = async (serviceName: string): Promise<ConnectionStatus> => {
    const service = services.find(s => s.name === serviceName);
    if (!service) {
      return { success: false, message: 'Service not found' };
    }

    // Update service status to checking
    setServices(prev => 
      prev.map(s => 
        s.name === serviceName 
          ? { ...s, status: 'checking', error: undefined }
          : s
      )
    );

    try {
      let endpoint = '';
      let testData = {};

      // Get current configuration first for the specific service
      const configResponse = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/settings.yaml`);
      const configData = await configResponse.json();
      const config = configData.config;

      if (!config || !config.api_keys) {
        throw new Error('Configuration not found');
      }

      // Prepare test request based on service type
      switch (serviceName) {
        case 'Jellyfin':
          if (!config.api_keys.Jellyfin?.[0]) {
            throw new Error('Jellyfin configuration not found');
          }
          endpoint = '/api/v1/config/test-jellyfin';
          testData = {
            url: config.api_keys.Jellyfin[0].url,
            api_key: config.api_keys.Jellyfin[0].api_key,
            user_id: config.api_keys.Jellyfin[0].user_id
          };
          break;

        case 'OMDB':
          if (!config.api_keys.OMDB?.[0]) {
            throw new Error('OMDB configuration not found');
          }
          endpoint = '/api/v1/config/test-omdb';
          testData = {
            api_key: config.api_keys.OMDB[0].api_key
          };
          break;

        case 'TMDB':
          if (!config.api_keys.TMDB?.[0]) {
            throw new Error('TMDB configuration not found');
          }
          endpoint = '/api/v1/config/test-tmdb';
          testData = {
            api_key: config.api_keys.TMDB[0].api_key
          };
          break;

        case 'MDBList':
          if (!config.api_keys.MDBList?.[0]) {
            throw new Error('MDBList configuration not found');
          }
          endpoint = '/api/v1/config/test-mdblist';
          testData = {
            api_key: config.api_keys.MDBList[0].api_key
          };
          break;

        case 'AniDB':
          if (!config.api_keys.aniDB) {
            throw new Error('AniDB configuration not found');
          }
          
          let username = '';
          let password = '';
          let client_name = 'aphrodite';
          let version = 1;
          
          // Handle both array and object formats
          if (Array.isArray(config.api_keys.aniDB)) {
            for (const item of config.api_keys.aniDB) {
              if (item && typeof item === 'object') {
                if (item.username) username = item.username;
                if (item.password) password = item.password;
                if (item.client_name) client_name = item.client_name;
                if (item.version) version = item.version;
              }
            }
          } else if (typeof config.api_keys.aniDB === 'object') {
            username = config.api_keys.aniDB.username || '';
            password = config.api_keys.aniDB.password || '';
            client_name = config.api_keys.aniDB.client_name || 'aphrodite';
            version = config.api_keys.aniDB.version || 1;
          }

          if (!username || !password) {
            throw new Error('AniDB credentials incomplete');
          }

          endpoint = '/api/v1/config/test-anidb';
          testData = {
            username,
            password,
            client_name,
            version
          };
          break;

        default:
          throw new Error('Unknown service');
      }

      // Make the test request
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}${endpoint}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(testData),
      });

      const result = await response.json();

      const connectionResult: ConnectionStatus = {
        success: response.ok && result.success !== false,
        message: result.message || (response.ok ? 'Connection successful!' : 'Connection failed')
      };

      // Update service status
      setServices(prev => 
        prev.map(s => 
          s.name === serviceName 
            ? { 
                ...s, 
                status: connectionResult.success ? 'connected' : 'failed',
                error: connectionResult.success ? undefined : connectionResult.message
              }
            : s
        )
      );

      return connectionResult;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Connection failed';
      
      // Update service status
      setServices(prev => 
        prev.map(s => 
          s.name === serviceName 
            ? { ...s, status: 'failed', error: errorMessage }
            : s
        )
      );

      return { success: false, message: errorMessage };
    }
  };

  // Test all connections
  const testAllConnections = async () => {
    setIsTestingAll(true);
    console.log('Starting connection check for all services');

    try {
      // Test each connection sequentially for better error handling
      for (const service of services) {
        console.log(`Testing connection for ${service.name}...`);
        try {
          await testConnection(service.name);
          console.log(`${service.name} connection check completed`);
        } catch (error) {
          console.error(`Error during ${service.name} connection check:`, error);
        }
      }

      toast.success('Connection tests completed');
    } catch (error) {
      console.error('Error during connection testing:', error);
      toast.error('Failed to complete connection tests');
    } finally {
      setIsTestingAll(false);
      console.log('All connection checks completed');
    }
  };

  return {
    services,
    isTestingAll,
    testConnection,
    testAllConnections,
    setServices
  };
}

// Database operations hook
export function useDatabaseOperations() {
  const [databaseInfo, setDatabaseInfo] = useState<DatabaseInfo | null>(null);
  const [loading, setLoading] = useState({
    info: false,
    backup: false,
    restore: false,
    verify: false,
    cleanup: false,
    export: false,
    integrity: false
  });

  // Load database info
  const loadDatabaseInfo = async () => {
    setLoading(prev => ({ ...prev, info: true }));
    
    try {
      console.log('Loading database info from:', `${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/database/status`);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/database/status`);
      
      console.log('Database info response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      
      console.log('Database info response data:', data);
      
      if (data.success) {
        setDatabaseInfo(data);
        console.log('Database info loaded successfully');
      } else {
        console.error('Database info request failed:', data);
        toast.error(`Failed to load database information: ${data.error || 'Unknown error'}`);
      }
    } catch (error) {
      console.error('Error loading database info:', error);
      toast.error(`Failed to load database information: ${error instanceof Error ? error.message : 'Unknown error'}`);
    } finally {
      setLoading(prev => ({ ...prev, info: false }));
    }
  };

  // Create backup
  const createBackup = async (options: { compress: boolean }): Promise<DatabaseOperationResult> => {
    setLoading(prev => ({ ...prev, backup: true }));
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/database/backup`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(options),
      });

      const data = await response.json();
      
      if (data.success) {
        toast.success(`Backup created: ${data.backup_filename}`);
        await loadDatabaseInfo(); // Refresh info
      } else {
        toast.error(`Backup failed: ${data.error}`);
      }

      return {
        success: data.success,
        message: data.success ? `Backup created: ${data.backup_filename}` : data.error,
        details: data
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Backup failed';
      toast.error(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(prev => ({ ...prev, backup: false }));
    }
  };

  // Restore backup
  const restoreBackup = async (filename: string): Promise<DatabaseOperationResult> => {
    setLoading(prev => ({ ...prev, restore: true }));
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/database/restore`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ filename }),
      });

      const data = await response.json();
      
      if (data.success) {
        toast.success('Database restored successfully');
        await loadDatabaseInfo(); // Refresh info
      } else {
        toast.error(`Restore failed: ${data.error}`);
      }

      return {
        success: data.success,
        message: data.success ? 'Database restored successfully' : data.error,
        details: data
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Restore failed';
      toast.error(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(prev => ({ ...prev, restore: false }));
    }
  };

  // Export database to JSON
  const exportDatabase = async (options: { includeSensitive: boolean }): Promise<DatabaseOperationResult> => {
    setLoading(prev => ({ ...prev, export: true }));
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/database/export`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(options),
      });

      if (response.ok) {
        // Handle file download
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        
        // Extract filename from Content-Disposition header
        const contentDisposition = response.headers.get('Content-Disposition');
        let filename = 'database_export.json';
        if (contentDisposition) {
          const filenameMatch = contentDisposition.match(/filename="?([^"]+)"?/);
          if (filenameMatch) {
            filename = filenameMatch[1];
          }
        }
        
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        toast.success('Database exported successfully');
        
        return {
          success: true,
          message: `Database exported successfully: ${filename}`
        };
      } else {
        const errorData = await response.json();
        toast.error(`Export failed: ${errorData.detail || 'Unknown error'}`);
        return {
          success: false,
          message: errorData.detail || 'Export failed'
        };
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Export failed';
      toast.error(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(prev => ({ ...prev, export: false }));
    }
  };

  // Import database settings from JSON
  const importDatabaseSettings = async (jsonData: any): Promise<DatabaseOperationResult> => {
    setLoading(prev => ({ ...prev, restore: true }));
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/database/import-settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ jsonData }),
      });

      const data = await response.json();
      
      if (data.success) {
        const summary = data.import_summary;
        toast.success(
          `Database settings imported successfully: ${summary.tables_imported} tables imported, ${summary.tables_skipped} skipped`,
          { duration: 6000 }
        );
        
        if (data.errors && data.errors.length > 0) {
          toast.warning(`Import completed with ${data.errors.length} errors. Check console for details.`);
          console.warn('Import errors:', data.errors);
        }
        
        await loadDatabaseInfo(); // Refresh info
      } else {
        toast.error(`Import failed: ${data.detail || 'Unknown error'}`);
      }

      return {
        success: data.success,
        message: data.success ? 'Database settings imported successfully' : (data.detail || 'Import failed'),
        details: data
      };
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Import failed';
      toast.error(errorMessage);
      return { success: false, message: errorMessage };
    } finally {
      setLoading(prev => ({ ...prev, restore: false }));
    }
  };

  return {
    databaseInfo,
    loading,
    loadDatabaseInfo,
    createBackup,
    restoreBackup,
    exportDatabase,
    importDatabaseSettings,
    setDatabaseInfo
  };
}

// Logs hook
export function useLogsViewer() {
  const [logs, setLogs] = useState<LogEntry[]>([]);
  const [fileInfo, setFileInfo] = useState<LogFileInfo | null>(null);
  const [availableLevels, setAvailableLevels] = useState<string[]>([]);
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  // Fetch logs
  const fetchLogs = useCallback(async () => {
    setIsLoading(true);
    setError('');
    
    try {
      const params = new URLSearchParams();
      if (selectedLevel && selectedLevel !== 'all') params.append('level', selectedLevel);
      if (searchQuery) params.append('search', searchQuery);
      params.append('limit', '1000');

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/logs?${params}`);
      const data = await response.json();
      
      if (data.success) {
        setLogs(data.logs || []);
        setFileInfo({
          total_lines: data.total_lines || 0,
          filtered_lines: data.filtered_lines || 0,
          file_size: data.file_size || 0,
          file_modified: data.file_modified || ''
        });
      } else {
        setError(data.message || 'Failed to load logs');
      }
    } catch (err) {
      console.error('Error fetching logs:', err);
      setError('Error loading logs');
    } finally {
      setIsLoading(false);
    }
  }, [selectedLevel, searchQuery]);

  // Fetch available log levels
  const fetchLogLevels = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/logs/levels`);
      const data = await response.json();
      
      if (data.success) {
        setAvailableLevels(data.levels || []);
      }
    } catch (err) {
      console.error('Error fetching log levels:', err);
    }
  };

  // Clear logs
  const clearLogs = useCallback(async (): Promise<boolean> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/logs/clear`, {
        method: 'DELETE'
      });
      
      const data = await response.json();
      
      if (data.success) {
        // Refresh logs after clearing to show the empty state
        await fetchLogs();
        toast.success('Logs cleared successfully');
        return true;
      } else {
        toast.error(`Failed to clear logs: ${data.error || data.message || 'Unknown error'}`);
        return false;
      }
    } catch (error) {
      console.error('Error clearing logs:', error);
      toast.error('Error clearing logs');
      return false;
    }
  }, [fetchLogs]);

  // Copy logs to clipboard
  const copyLogs = async () => {
    if (!logs.length) return;
    
    try {
      const logText = logs.map(log => 
        `${log.timestamp} - ${log.level} - ${log.message}`
      ).join('\n');
      
      await navigator.clipboard.writeText(logText);
      toast.success('Logs copied to clipboard!');
    } catch (err) {
      console.error('Error copying logs:', err);
      toast.error('Failed to copy logs to clipboard');
    }
  };

  // Download logs
  const downloadLogs = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/maintenance/logs/download`);
      
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `aphrodite-logs-${new Date().toISOString().split('T')[0]}.log`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        toast.success('Logs downloaded successfully');
      } else {
        toast.error('Failed to download logs');
      }
    } catch (error) {
      console.error('Error downloading logs:', error);
      toast.error('Error downloading logs');
    }
  };

  return {
    logs,
    fileInfo,
    availableLevels,
    selectedLevel,
    searchQuery,
    isLoading,
    error,
    setSelectedLevel,
    setSearchQuery,
    fetchLogs,
    fetchLogLevels,
    clearLogs,
    copyLogs,
    downloadLogs
  };
}
