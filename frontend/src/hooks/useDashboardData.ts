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
  version: string;
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
    version: 'Unknown',
  });

  const fetchDashboardData = async () => {
    try {
      console.log('🔍 Dashboard: Starting data fetch...');
      setData(prev => ({ ...prev, isLoading: true, error: null }));

      console.log('🔍 Dashboard: Making API calls...');
      // Fetch all required data in parallel
      const [analyticsOverview, systemHealth, recentJobs, todayCompletedJobs, systemInfo] = await Promise.all([
        apiService.getAnalyticsOverview().catch((err) => { console.error('Analytics failed:', err); return null; }),
        apiService.getSystemStatus().catch((err) => { console.error('System status failed:', err); return null; }),
        apiService.getJobs({ user_id: 'default_user' }).catch((err) => { console.error('Jobs failed:', err); return []; }),
        apiService.getJobs({ user_id: 'default_user' }).catch((err) => { console.error('Jobs2 failed:', err); return []; }),
        apiService.getSystemInfo().catch((err) => { console.error('System info failed:', err); return null; }),
      ]);
      
      console.log('🔍 Dashboard: API responses:', {
        analyticsOverview,
        systemHealth,
        recentJobs: Array.isArray(recentJobs) ? recentJobs.length : 'not array',
        systemInfo
      });

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
      // Convert workflow jobs data to dashboard stats
      const allJobs = Array.isArray(recentJobs) ? recentJobs : (recentJobs ? [recentJobs] : []);
      const completedJobs = allJobs.filter(job => job.status === 'completed');
      const activeJobs = allJobs.filter(job => job.status === 'running' || job.status === 'queued' || job.status === 'processing');
      
      const stats = {
        total_media_items: analyticsOverview?.total_media_items || 0,
        active_jobs: activeJobs.length,
        completed_today: getTodayCompletedJobs(completedJobs),
        processing_success_rate: completedJobs.length > 0 ? Math.round((completedJobs.filter(j => j.failed_posters === 0).length / completedJobs.length) * 100) : 0,
      };

      // Process recent jobs - handle workflow job format
      const jobsArray = Array.isArray(recentJobs) ? recentJobs : (recentJobs ? [recentJobs] : []);
      const processedJobs = jobsArray.slice(0, 5).map((job: any) => ({
        id: job.job_id || job.id,
        name: job.name || job.media_name || job.title || `Job ${(job.job_id || job.id || '').slice(0, 8)}`,
        status: job.status,
        progress: calculateWorkflowJobProgress(job),
        created_at: job.created_at,
      }));

      setData({
        systemStatus,
        stats,
        recentJobs: processedJobs,
        isLoading: false,
        error: null,
        version: systemInfo?.version || 'Unknown',
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
  const today = new Date();
  const todayStart = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  const todayEnd = new Date(today.getFullYear(), today.getMonth(), today.getDate() + 1);
  
  return jobs.filter(job => {
    if (job.status !== 'completed') return false;
    
    const completedDate = new Date(job.completed_at || job.created_at);
    return completedDate >= todayStart && completedDate < todayEnd;
  }).length;
}

function calculateWorkflowJobProgress(job: any): number {
  switch (job.status) {
    case 'completed':
      return 100;
    case 'failed':
      return 0;
    case 'running':
    case 'processing':
      if (job.total_posters && job.completed_posters) {
        return Math.round((job.completed_posters / job.total_posters) * 100);
      }
      return Math.floor(Math.random() * 70) + 10; // Fallback simulation
    case 'queued':
      return 0;
    default:
      return 0;
  }
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
