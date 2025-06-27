/**
 * API Service for Aphrodite v2 Frontend
 * Handles all HTTP requests to the backend API
 */

// Use the current page's origin for API calls, falling back to localhost for development
const getApiBaseUrl = () => {
  // If explicitly set via environment variable, use that
  if (process.env.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }
  
  // In browser, use current origin (same host as frontend)
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  
  // Fallback for server-side rendering or development
  return 'http://localhost:8000';
};

const API_BASE_URL = getApiBaseUrl();

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public response?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

async function handleResponse(response: Response) {
  console.log(`🌐 API Response: ${response.status} ${response.url}`);
  
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.error || errorData.message || errorMessage;
    } catch {
      // If we can't parse the error response, use the default message
    }
    console.error(`❌ API Error: ${errorMessage} (${response.url})`);
    throw new ApiError(errorMessage, response.status);
  }
  
  try {
    const data = await response.json();
    console.log(`✅ API Success: ${response.url}`);
    return data;
  } catch {
    // If there's no JSON response, return empty object
    console.log(`⚠️ API No JSON: ${response.url}`);
    return {};
  }
}

export const apiService = {
  // Configuration endpoints
  async getConfig(filename: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/config/${filename}`);
    return handleResponse(response);
  },

  async updateConfig(filename: string, config: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/config/${filename}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return handleResponse(response);
  },

  async getConfigFiles() {
    const response = await fetch(`${API_BASE_URL}/api/v1/config/files`);
    return handleResponse(response);
  },

  // Connection testing
  async testJellyfinConnection(config: {
    url: string;
    api_key: string;
    user_id: string;
  }) {
    const response = await fetch(`${API_BASE_URL}/api/v1/config/test-jellyfin`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return handleResponse(response);
  },

  async testConnection(service: string, config: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/config/test-${service}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(config),
    });
    return handleResponse(response);
  },

  // System endpoints
  async getSystemStatus() {
    const response = await fetch(`${API_BASE_URL}/health/detailed`);
    return handleResponse(response);
  },

  async getSystemInfo() {
    const response = await fetch(`${API_BASE_URL}/api/v1/system/info`);
    return handleResponse(response);
  },

  async getSystemConfig() {
    const response = await fetch(`${API_BASE_URL}/api/v1/config/system`);
    return handleResponse(response);
  },

  // Preview endpoints
  async getPreviewBadgeTypes() {
    const response = await fetch(`${API_BASE_URL}/api/v1/preview/badge-types`);
    return handleResponse(response);
  },

  async generatePreview(request: { badgeTypes: string[] }) {
    const response = await fetch(`${API_BASE_URL}/api/v1/preview/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    });
    return handleResponse(response);
  },

  async getPreviewLibraries() {
    const response = await fetch(`${API_BASE_URL}/api/v1/preview/libraries`);
    return handleResponse(response);
  },

  async getPreviewMedia(params?: {
    library_id?: string;
    search?: string;
    page?: number;
    limit?: number;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.library_id) searchParams.set('library_id', params.library_id);
    if (params?.search) searchParams.set('search', params.search);
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());

    const url = `${API_BASE_URL}/api/v1/preview/media${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  // Media endpoints
  async getMedia(params?: {
    page?: number;
    per_page?: number;
    search?: string;
    media_type?: string;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
    if (params?.search) searchParams.set('search', params.search);
    if (params?.media_type) searchParams.set('media_type', params.media_type);

    const url = `${API_BASE_URL}/api/v1/media${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  async getMediaItem(id: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/media/${id}`);
    return handleResponse(response);
  },

  async scanLibrary() {
    const response = await fetch(`${API_BASE_URL}/api/v1/media/scan`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  // Jobs endpoints (using workflow API)
  async getJobs(params?: {
    page?: number;
    per_page?: number;
    status?: string;
    user_id?: string;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.user_id) searchParams.set('user_id', params.user_id);
    // Note: workflow API doesn't support page/per_page/status filtering like the regular jobs API

    const url = `${API_BASE_URL}/api/v1/workflow/jobs/${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  async createJob(data: {
    media_ids: string[];
    job_type: string;
    parameters?: any;
  }) {
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  async getJob(id: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/workflow/jobs/${id}`);
    return handleResponse(response);
  },

  // Schedule endpoints
  async getSchedules(params?: {
    skip?: number;
    limit?: number;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());

    const url = `${API_BASE_URL}/api/v1/schedules${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  async createSchedule(schedule: {
    name: string;
    timezone: string;
    cron_expression: string;
    badge_types: string[];
    reprocess_all: boolean;
    enabled: boolean;
    target_libraries: string[];
  }) {
    const response = await fetch(`${API_BASE_URL}/api/v1/schedules`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(schedule),
    });
    return handleResponse(response);
  },

  async updateSchedule(id: string, schedule: any) {
    const response = await fetch(`${API_BASE_URL}/api/v1/schedules/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(schedule),
    });
    return handleResponse(response);
  },

  async deleteSchedule(id: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/schedules/${id}`, {
      method: 'DELETE',
    });
    return handleResponse(response);
  },

  async getScheduleHistory(params?: {
    skip?: number;
    limit?: number;
    schedule_id?: string;
    status?: string;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.skip) searchParams.set('skip', params.skip.toString());
    if (params?.limit) searchParams.set('limit', params.limit.toString());
    if (params?.schedule_id) searchParams.set('schedule_id', params.schedule_id);
    if (params?.status) searchParams.set('status', params.status);

    const url = `${API_BASE_URL}/api/v1/schedules/executions/history${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
    const response = await fetch(url);
    return handleResponse(response);
  },

  async executeSchedule(id: string) {
    const response = await fetch(`${API_BASE_URL}/api/v1/schedules/${id}/execute`, {
      method: 'POST',
    });
    return handleResponse(response);
  },

  async getScheduleBadgeTypes() {
    const response = await fetch(`${API_BASE_URL}/api/v1/schedules/config/badge-types`);
    return handleResponse(response);
  },

  async getScheduleCronPresets() {
    const response = await fetch(`${API_BASE_URL}/api/v1/schedules/config/cron-presets`);
    return handleResponse(response);
  },

  async getScheduleLibraries() {
    const response = await fetch(`${API_BASE_URL}/api/v1/schedules/config/libraries`);
    return handleResponse(response);
  },

  // Analytics endpoints
  async getAnalyticsOverview() {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/overview`);
    return handleResponse(response);
  },

  async getJobStatusDistribution() {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/jobs/status-distribution`);
    return handleResponse(response);
  },

  async getProcessingTrends(days: number = 30) {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/jobs/trends?days=${days}`);
    return handleResponse(response);
  },

  async getJobTypeDistribution() {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/jobs/types`);
    return handleResponse(response);
  },

  async getScheduleAnalytics() {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/schedules`);
    return handleResponse(response);
  },

  async getSystemPerformance() {
    const response = await fetch(`${API_BASE_URL}/api/v1/analytics/performance`);
    return handleResponse(response);
  },
};

export default apiService;