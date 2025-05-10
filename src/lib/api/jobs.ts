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

export interface CreateJobParams {
  user_id: number;
  name: string;
  items: Array<{
    jellyfin_item_id: string;
    title: string;
  }>;
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
    const response = await fetch('/api/jobs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify(params)
    });

    if (!response.ok) {
      throw new Error(`Failed to create job: ${response.statusText}`);
    }

    return response.json();
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
