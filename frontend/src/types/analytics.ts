/**
 * Analytics data types for Aphrodite v2
 */

export interface AnalyticsOverview {
  total_jobs: number;
  completed_jobs: number;
  failed_jobs: number;
  queued_jobs: number;
  running_jobs: number;
  total_schedules: number;
  active_schedules: number;
  total_media_items: number;
  processing_success_rate: number;
}

export interface JobStatusDistribution {
  status: string;
  count: number;
  percentage: number;
}

export interface ProcessingTrend {
  date: string;
  completed: number;
  failed: number;
  created: number;
}

export interface ScheduleAnalytics {
  id: string;
  name: string;
  enabled: boolean;
  badge_types: string[];
  target_libraries: string[];
  last_execution: string | null;
  execution_count: number;
  success_rate: number;
}

export interface JobTypeDistribution {
  job_type: string;
  count: number;
  success_rate: number;
  avg_duration_seconds: number | null;
}

export interface SystemPerformance {
  avg_job_duration_seconds: number | null;
  jobs_per_hour_24h: number;
  peak_hour_jobs: number;
  peak_hour: number;
  queue_health_score: number;
}
