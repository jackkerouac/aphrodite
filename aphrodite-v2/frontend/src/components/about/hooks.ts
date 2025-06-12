import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { 
  AboutPageData, 
  defaultAboutPageData,
  SystemInfo,
  UpdateInfo,
  HealthStatus,
  SystemStats,
  LogEntry
} from './types';

export function useAboutData() {
  const [loading, setLoading] = useState(false);
  const [checkingUpdates, setCheckingUpdates] = useState(false);
  const [data, setData] = useState<AboutPageData>(defaultAboutPageData);

  // Load all about page data
  const loadAboutData = async () => {
    setLoading(true);
    
    try {
      console.log('Loading about page data...');
      
      // Load system info, health status, and stats in parallel
      const [systemResponse, healthResponse, statsResponse, logsResponse] = await Promise.all([
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/system/info`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/system/health`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/system/stats`),
        fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/system/logs`)
      ]);

      // Parse responses
      const systemData = await systemResponse.json();
      const healthData = await healthResponse.json();
      const statsData = await statsResponse.json();
      const logsData = await logsResponse.json();

      console.log('Loaded about data:', { systemData, healthData, statsData, logsData });

      // Update state with loaded data
      setData(prev => ({
        ...prev,
        systemInfo: systemData.success ? {
          version: systemData.version,
          execution_mode: systemData.execution_mode,
          database_schema_hash: systemData.database_schema_hash,
          uptime: systemData.uptime
        } : prev.systemInfo,
        healthStatus: healthData.success ? {
          status: healthData.status,
          services: healthData.services,
          timestamp: healthData.timestamp
        } : prev.healthStatus,
        stats: statsData.success ? {
          total_jobs: statsData.total_jobs,
          successful_jobs: statsData.successful_jobs,
          failed_jobs: statsData.failed_jobs,
          success_rate: statsData.success_rate,
          total_media_processed: statsData.total_media_processed,
          database_size: statsData.database_size
        } : prev.stats,
        recentLogs: logsData.success ? logsData.logs : prev.recentLogs
      }));

      console.log('About page data loaded successfully');
    } catch (error) {
      console.error('Error loading about page data:', error);
      toast.error('Failed to load system information', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
    } finally {
      setLoading(false);
    }
  };

  // Check for updates
  const checkForUpdates = async () => {
    setCheckingUpdates(true);
    
    try {
      console.log('Checking for updates...');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/system/check-updates`);
      const updateData = await response.json();
      
      console.log('Update check response:', updateData);
      
      if (updateData.success) {
        setData(prev => ({
          ...prev,
          updateInfo: {
            update_available: updateData.update_available,
            current_version: updateData.current_version,
            latest_version: updateData.latest_version,
            message: updateData.message,
            release_notes_url: updateData.release_notes_url
          }
        }));

        if (!updateData.update_available) {
          toast.success('You are running the latest version!', {
            duration: 3000
          });
        } else {
          toast.info(`Update available: v${updateData.latest_version}`, {
            description: 'A new version is available for download.',
            duration: 5000
          });
        }
      }
    } catch (error) {
      console.error('Error checking for updates:', error);
      toast.error('Failed to check for updates', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
    } finally {
      setCheckingUpdates(false);
    }
  };

  // Refresh system data (reload everything)
  const refreshData = async () => {
    await loadAboutData();
  };

  return {
    loading,
    checkingUpdates,
    data,
    loadAboutData,
    checkForUpdates,
    refreshData
  };
}

// Separate hook for just system info (lightweight)
export function useSystemInfo() {
  const [loading, setLoading] = useState(false);
  const [systemInfo, setSystemInfo] = useState<SystemInfo>(defaultAboutPageData.systemInfo);

  const loadSystemInfo = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/system/info`);
      const data = await response.json();
      
      if (data.success) {
        setSystemInfo({
          version: data.version,
          execution_mode: data.execution_mode,
          database_schema_hash: data.database_schema_hash,
          uptime: data.uptime
        });
      }
    } catch (error) {
      console.error('Error loading system info:', error);
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    systemInfo,
    loadSystemInfo
  };
}

// Separate hook for health status (for real-time updates)
export function useHealthStatus() {
  const [loading, setLoading] = useState(false);
  const [healthStatus, setHealthStatus] = useState<HealthStatus>(defaultAboutPageData.healthStatus);

  const loadHealthStatus = async () => {
    setLoading(true);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/system/health`);
      const data = await response.json();
      
      if (data.success) {
        setHealthStatus({
          status: data.status,
          services: data.services,
          timestamp: data.timestamp
        });
      }
    } catch (error) {
      console.error('Error loading health status:', error);
    } finally {
      setLoading(false);
    }
  };

  return {
    loading,
    healthStatus,
    loadHealthStatus
  };
}
