import axios from 'axios';

const baseURL = process.env.VUE_APP_API_URL || 'http://localhost:5000';

// Create axios instance
const axiosInstance = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  timeout: 10000
});

export default {
  // Job related API methods
  getJobs: (page = 1, perPage = 20, jobType = null) => {
    let url = `/api/jobs/?page=${page}&per_page=${perPage}`;
    if (jobType) {
      url += `&type=${jobType}`;
    }
    return axiosInstance.get(url);
  },

  getJob: (jobId) => axiosInstance.get(`/api/jobs/${jobId}`),

  getJobItems: (jobId, page = 1, perPage = 20) => 
    axiosInstance.get(`/api/jobs/${jobId}/items?page=${page}&per_page=${perPage}`),

  deleteJob: (jobId) => axiosInstance.delete(`/api/jobs/${jobId}`),

  // Image related API methods
  getImages: (page = 1, perPage = 20) => 
    axiosInstance.get(`/api/images/list?page=${page}&per_page=${perPage}`),

  getImageUrl: (type, filename) => `${baseURL}/api/images/${type}/${filename}`,

  getImageBase64: (type, filename) => 
    axiosInstance.get(`/api/images/base64/${type}/${filename}`),

  getImagePath: (path) => `${baseURL}/api/images/serve?path=${encodeURIComponent(path)}`,

  downloadImage: (filename) => `${baseURL}/api/images/download/${filename}`
};
