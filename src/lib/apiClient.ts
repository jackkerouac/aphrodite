// Configure the base URL for the API client
// This should come from environment variables in a real application
const API_BASE_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:5000/api';

// Helper function to handle API responses
const handleResponse = async (response: Response) => {
  // Log response in development
  if (process.env.NODE_ENV !== 'production') {
    console.log(`✅ API Response: ${response.url}`, response.status);
  }
  
  if (!response.ok) {
    const error = await response.json().catch(() => ({
      message: 'Failed to parse error response'
    }));
    
    throw new Error(error.message || `Request failed with status ${response.status}`);
  }
  
  return response.json();
};

// Helper function to make API requests
const makeRequest = async (url: string, options: RequestInit = {}) => {
  const fullUrl = `${API_BASE_URL}${url.startsWith('/') ? url : `/${url}`}`;
  
  // Log outgoing requests in development
  if (process.env.NODE_ENV !== 'production') {
    console.log(`🔷 API Request: ${options.method || 'GET'} ${fullUrl}`, options.body || '');
  }
  
  try {
    const response = await fetch(fullUrl, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
      },
    });
    
    return handleResponse(response);
  } catch (error) {
    // Log error details
    if (process.env.NODE_ENV !== 'production') {
      console.error('❌ API Request Error:', {
        url: fullUrl,
        method: options.method,
        error,
      });
    }
    
    throw error;
  }
};

// API client
export const apiClient = {
  get: (url: string, options: RequestInit = {}) => {
    return makeRequest(url, { ...options, method: 'GET' });
  },
  
  post: (url: string, data: any = {}, options: RequestInit = {}) => {
    return makeRequest(url, {
      ...options,
      method: 'POST',
      body: JSON.stringify(data),
    });
  },
  
  put: (url: string, data: any = {}, options: RequestInit = {}) => {
    return makeRequest(url, {
      ...options,
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },
  
  delete: (url: string, options: RequestInit = {}) => {
    return makeRequest(url, { ...options, method: 'DELETE' });
  },
  
  patch: (url: string, data: any = {}, options: RequestInit = {}) => {
    return makeRequest(url, {
      ...options,
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  },
};
