export interface Job {
  id: number;
  user_id: number;
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  items_total: number;
  items_processed: number;
  items_failed: number;
  created_at: string;
  updated_at: string;
  completed_at?: string;
}

export interface JobItem {
  id: number;
  job_id: number;
  jellyfin_item_id: string;
  title: string;
  status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
  updated_at: string;
}

// Use the UnifiedBadgeSettings structure directly to ensure consistency
// This is the exact same structure used by the unified badge settings system
export interface JobBadgeSetting {
  // Primary fields
  badge_type: string;
  badge_size: number;
  badge_position: string;
  
  // Visual appearance
  background_color: string;
  background_opacity: number;
  display_format?: string; // Only for review badges
  
  // Border settings
  border_radius: number;
  border_width: number;
  border_color: string;
  border_opacity: number;
  
  // Shadow settings
  shadow_enabled: boolean;
  shadow_color: string;
  shadow_blur: number;
  shadow_offset_x: number;
  shadow_offset_y: number;
  
  // Spacing
  edge_padding?: number;
  
  // Badge-specific properties
  properties: Record<string, any>;
}

export interface CreateJobParams {
  user_id: number;
  name: string;
  items: Array<{
    jellyfin_item_id: string;
    title: string;
  }>;
  badgeSettings?: JobBadgeSetting[];
}

export interface JobsResponse {
  jobs: Job[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

export interface JobItemsResponse {
  items: JobItem[];
  total: number;
  page: number;
  limit: number;
  totalPages: number;
}

const jobsApi = {
  async getJobs(userId: string, page: number = 1, limit: number = 10): Promise<JobsResponse> {
    const queryParams = new URLSearchParams({
      userId,
      page: page.toString(),
      limit: limit.toString()
    });

    const response = await fetch(`/api/jobs?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch jobs: ${response.statusText}`);
    }

    return response.json();
  },

  async createJob(params: CreateJobParams): Promise<Job> {
    try {
      console.log('Sending job creation request:', params);
      
      const response = await fetch('/api/jobs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(params)
      });

      const responseText = await response.text();
      console.log('Server response:', responseText);

      if (!response.ok) {
        throw new Error(`Failed to create job: ${response.statusText} - ${responseText}`);
      }

      try {
        return JSON.parse(responseText);
      } catch (parseError) {
        console.error('Failed to parse response:', parseError);
        throw new Error(`Failed to parse server response: ${parseError}`);
      }
    } catch (error) {
      console.error('Error creating job:', error);
      throw error;
    }
  },

  async getJob(jobId: number, userId: string): Promise<Job> {
    const queryParams = new URLSearchParams({ userId });

    const response = await fetch(`/api/jobs/${jobId}?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch job: ${response.statusText}`);
    }

    return response.json();
  },

  async updateJobStatus(
    jobId: number, 
    status: Job['status'], 
    updates?: Partial<Pick<Job, 'items_processed' | 'items_failed'>>
  ): Promise<Job> {
    const response = await fetch(`/api/jobs/${jobId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ status, ...updates })
    });

    if (!response.ok) {
      throw new Error(`Failed to update job: ${response.statusText}`);
    }

    return response.json();
  },

  async getJobItems(jobId: number, page: number = 1, limit: number = 50): Promise<JobItemsResponse> {
    const queryParams = new URLSearchParams({
      page: page.toString(),
      limit: limit.toString()
    });

    const response = await fetch(`/api/jobs/${jobId}/items?${queryParams}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to fetch job items: ${response.statusText}`);
    }

    return response.json();
  },

  async startProcessing(jobId: number): Promise<{ message: string; jobId: number }> {
    const response = await fetch(`/api/jobs/${jobId}/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include'
    });

    if (!response.ok) {
      throw new Error(`Failed to start job processing: ${response.statusText}`);
    }

    return response.json();
  }
};

export default jobsApi;
