/**
 * API Service for Aphrodite v2 Frontend
 * Handles all HTTP requests to the backend API
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

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
  if (!response.ok) {
    let errorMessage = `HTTP ${response.status}: ${response.statusText}`;
    try {
      const errorData = await response.json();
      errorMessage = errorData.error || errorData.message || errorMessage;
    } catch {
      // If we can't parse the error response, use the default message
    }
    throw new ApiError(errorMessage, response.status);
  }
  
  try {
    return await response.json();
  } catch {
    // If there's no JSON response, return empty object
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
    const response = await fetch(`${API_BASE_URL}/health`);
    return handleResponse(response);
  },

  async getSystemConfig() {
    const response = await fetch(`${API_BASE_URL}/api/v1/config/system`);
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

  // Job endpoints
  async getJobs(params?: {
    page?: number;
    per_page?: number;
    status?: string;
  }) {
    const searchParams = new URLSearchParams();
    if (params?.page) searchParams.set('page', params.page.toString());
    if (params?.per_page) searchParams.set('per_page', params.per_page.toString());
    if (params?.status) searchParams.set('status', params.status);

    const url = `${API_BASE_URL}/api/v1/jobs${searchParams.toString() ? '?' + searchParams.toString() : ''}`;
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
    const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${id}`);
    return handleResponse(response);
  },
};

export default apiService;