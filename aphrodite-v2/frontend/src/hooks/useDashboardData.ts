/**
 * Custom hook for fetching dashboard data
 * Combines analytics and system status data for the main dashboard
 */

import { useState, useEffect } from 'react';
import { apiService } from '@/services/api';

export interface DashboardData {
  systemStatus: {
    api_status: 'online' | 'offline';
    jellyfin_status: 'connected' | 'disconnected';
    database_status: 'healthy' | 'unhealthy';
    queue_status: 'healthy' | 'unhealthy';
    uptime: string;
    workers_active: number;
  };
  stats: {
    total_media_items: number;
    active_jobs: number;
    completed_today: number;
    processing_success_rate: number;
  };
  recentJobs: Array<{
    id: string;
    name: string;
    status: 'running' | 'queued' | 'completed' | 'failed';
    progress: number;
    created_at: string;
  }>;
  isLoading: boolean;
  error: string | null;
}

export function useDashboardData(): DashboardData {
  const [data, setData] = useState<DashboardData>({
    systemStatus: {
      api_status: 'offline',
      jellyfin_status: 'disconnected',
      database_status: 'unhealthy',
      queue_status: 'unhealthy',
      uptime: '0h 0m',
      workers_active: 0,
    },
    stats: {
      total_media_items: 0,
      active_jobs: 0,
      completed_today: 0,
      processing_success_rate: 0,
    },
    recentJobs: [],
    isLoading: true,
    error: null,
  });

  const fetchDashboardData = async () => {
    try {
      setData(prev => ({ ...prev, isLoading: true, error: null }));

      // Fetch all required data in parallel
      const [analyticsOverview, systemHealth, recentJobs] = await Promise.all([
        apiService.getAnalyticsOverview().catch(() => null),
        apiService.getSystemStatus().catch(() => null),
        apiService.getJobs({ page: 1, per_page: 3, status: undefined }).catch(() => []),
      ]);

      // Process system status
      const systemStatus = {
        api_status: systemHealth?.status === 'healthy' ? 'online' as const : 'offline' as const,
        jellyfin_status: systemHealth?.components?.database?.status === 'healthy' ? 'connected' as const : 'disconnected' as const,
        database_status: systemHealth?.components?.database?.status === 'healthy' ? 'healthy' as const : 'unhealthy' as const,
        queue_status: systemHealth?.components?.redis?.status === 'healthy' ? 'healthy' as const : 'unhealthy' as const,
        uptime: formatUptime(systemHealth?.timestamp),
        workers_active: 2, // This would come from worker status in a real implementation
      };

      // Process analytics stats
      const stats = {
        total_media_items: analyticsOverview?.total_media_items || 0,
        active_jobs: (analyticsOverview?.running_jobs || 0) + (analyticsOverview?.queued_jobs || 0),
        completed_today: getTodayCompletedJobs(recentJobs || []),
        processing_success_rate: analyticsOverview?.processing_success_rate || 0,
      };

      // Process recent jobs
      const processedJobs = (recentJobs || []).slice(0, 3).map((job: any) => ({
        id: job.id,
        name: job.media_name || `Job ${job.id.slice(0, 8)}`,
        status: job.status,
        progress: calculateJobProgress(job),
        created_at: job.created_at,
      }));

      setData({
        systemStatus,
        stats,
        recentJobs: processedJobs,
        isLoading: false,
        error: null,
      });

    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setData(prev => ({
        ...prev,
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to fetch dashboard data',
      }));
    }
  };

  useEffect(() => {
    fetchDashboardData();
    
    // Set up polling for real-time updates
    const interval = setInterval(fetchDashboardData, 30000); // Update every 30 seconds
    
    return () => clearInterval(interval);
  }, []);

  return data;
}

// Helper functions
function formatUptime(timestamp: string | undefined): string {
  if (!timestamp) return '0h 0m';
  
  const start = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - start.getTime();
  
  const hours = Math.floor(diffMs / (1000 * 60 * 60));
  const minutes = Math.floor((diffMs % (1000 * 60 * 60)) / (1000 * 60));
  const days = Math.floor(hours / 24);
  
  if (days > 0) {
    return `${days}d ${hours % 24}h ${minutes}m`;
  }
  return `${hours}h ${minutes}m`;
}

function getTodayCompletedJobs(jobs: any[]): number {
  const today = new Date().toDateString();
  return jobs.filter(job => 
    job.status === 'completed' && 
    new Date(job.completed_at || job.created_at).toDateString() === today
  ).length;
}

function calculateJobProgress(job: any): number {
  switch (job.status) {
    case 'completed':
      return 100;
    case 'failed':
      return 0;
    case 'running':
      // In a real implementation, this would come from job progress tracking
      return Math.floor(Math.random() * 70) + 10; // Simulate progress between 10-80%
    case 'queued':
      return 0;
    default:
      return 0;
  }
}
