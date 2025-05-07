import { fetchApi } from '../api-client';

export const logs = {
  getLogs: async (params: { level?: string; limit?: number; page?: number } = {}): Promise<any> => {
    try {
      console.log('🔧 [apiClient] Fetching logs with params:', params);

      const queryParams = new URLSearchParams();
      if (params.level) queryParams.append('level', params.level);
      if (params.limit) queryParams.append('limit', params.limit.toString());
      if (params.page) queryParams.append('page', params.page.toString());

      const queryString = queryParams.toString();
      const endpoint = `/logs${queryString ? `?${queryString}` : ''}`;

      try {
        const data = await fetchApi<any>(endpoint);
        console.log('🔧 [apiClient] Received logs data:', data);

        if (!data) {
          return { logs: [], total: 0 };
        }

        if (!data.logs && Array.isArray(data)) {
          return { logs: data, total: data.length };
        }

        return data;
      } catch (error) {
        console.error('🔧 [apiClient] JSON parse error in logs response:', error);
        return { logs: [], total: 0 };
      }
    } catch (error) {
      console.error('❌ [apiClient] Error fetching logs:', error);
      return { logs: [], total: 0 };
    }
  },

  clearLogs: async (): Promise<any> => {
    try {
      console.log('🔧 [apiClient] Clearing logs...');
      const data = await fetchApi<any>('/logs/clear', {
        method: 'POST'
      });
      console.log('🔧 [apiClient] Logs cleared successfully');
      return data;
    } catch (error) {
      console.error('❌ [apiClient] Error clearing logs:', error);
      throw error;
    }
  }
};