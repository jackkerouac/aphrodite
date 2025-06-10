import apiClient from './index';

export default {
  /**
   * Get logs with optional filtering
   */
  getLogs(params = {}) {
    return apiClient.get('/api/logs/', { params });
  },

  /**
   * Get available log levels
   */
  getLogLevels() {
    return apiClient.get('/api/logs/levels');
  },

  /**
   * Clear all logs
   */
  clearLogs() {
    return apiClient.post('/api/logs/clear');
  },

  /**
   * Download logs as text
   */
  downloadLogs() {
    return apiClient.get('/api/logs/download');
  }
};
