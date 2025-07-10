export interface SystemOverview {
  analysis_period: {
    days: number;
    start_date: string;
    end_date: string;
  };
  overall_statistics: {
    totals: {
      total_activities: number;
      successful: number;
      failed: number;
      pending: number;
      success_rate: number;
    };
    performance: {
      average_processing_time_ms: number | null;
    };
    scope: {
      unique_users: number;
      unique_media_items: number;
    };
    activity_type_breakdown: Array<{
      activity_type: string;
      total: number;
      successful: number;
      failed: number;
      success_rate: number;
    }>;
  };
  recent_batches: {
    count: number;
    batches: Array<{
      batch_job_id: string;
      total_activities: number;
      successful: number;
      failed: number;
      success_rate: number;
      start_time: string | null;
      batch_duration_ms: number | null;
    }>;
  };
  top_users: {
    count: number;
    users: Array<{
      user_id: string;
      total_activities: number;
      successful: number;
      failed: number;
      success_rate: number;
    }>;
  };
  summary: {
    total_activities: number;
    success_rate: number;
    active_users: number;
    active_batches: number;
  };
}

export interface ActivitySearchParams {
  activity_types?: string[];
  statuses?: string[];
  success?: boolean;
  user_id?: string;
  start_date?: string;
  end_date?: string;
  error_text?: string;
  sort_by?: string;
  sort_order?: string;
  limit?: number;
  offset?: number;
  include_details?: boolean;
}

export interface SearchResult {
  activities: any[];
  pagination: {
    total_count: number;
    returned_count: number;
    limit: number;
    offset: number;
    has_next: boolean;
    has_prev: boolean;
    total_pages: number;
    current_page: number;
  };
}
