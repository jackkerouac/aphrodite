import { fetchApi, ApiError } from '../api-client';

export const resolutionBadge = {
  getSettings: async (userId: string = '1'): Promise<any> => {
    try {
      console.log('🔧 [apiClient] Fetching Resolution Badge settings...');
      const data = await fetchApi<any>(`/resolution-badge-settings/${userId}`);
      console.log('🔧 [apiClient] Received Resolution Badge settings:', data);
      return data;
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        console.log('❗ No Resolution Badge settings found, using defaults');
        return {
          size: 100,
          margin: 10,
          position: 'top-left',
          resolution_type: '1080',
          background_color: '#ffffff',
          background_transparency: 0.7,
          border_radius: 5,
          border_width: 1,
          border_color: '#000000',
          border_transparency: 0.9,
          shadow_toggle: false,
          shadow_color: '#000000',
          shadow_blur_radius: 5,
          shadow_offset_x: 0,
          shadow_offset_y: 0,
          z_index: 10
        };
      }
      console.error('❌ [apiClient] Resolution Badge settings error:', error);
      throw error;
    }
  },

  saveSettings: async (settings: any, userId: string = '1'): Promise<void> => {
    console.log('📤 [apiClient] Saving Resolution Badge settings:', settings);

    const requiredFields = [
      'size',
      'margin',
      'position',
      'resolution_type',
      'background_color',
      'background_transparency',
      'border_radius',
      'border_width',
      'border_color',
      'border_transparency',
      'z_index'
    ];

    const missingFields = [];
    for (const field of requiredFields) {
      const value = settings[field];
      if (value === undefined || value === null || value === '') {
        missingFields.push(field);
      }
    }

    if (missingFields.length > 0) {
      console.error('🚫 [apiClient] Missing required fields:', missingFields);
      console.error('🚫 [apiClient] Current settings values:', settings);
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }

    const settingsToSend = {
      size: Number(settings.size),
      margin: Number(settings.margin),
      position: String(settings.position),
      resolution_type: String(settings.resolution_type),
      background_color: String(settings.background_color),
      background_transparency: Number(settings.background_transparency),
      border_radius: Number(settings.border_radius),
      border_width: Number(settings.border_width),
      border_color: String(settings.border_color),
      border_transparency: Number(settings.border_transparency),
      shadow_toggle: Boolean(settings.shadow_toggle),
      shadow_color: String(settings.shadow_color || '#000000'),
      shadow_blur_radius: Number(settings.shadow_blur_radius || 0),
      shadow_offset_x: Number(settings.shadow_offset_x || 0),
      shadow_offset_y: Number(settings.shadow_offset_y || 0),
      z_index: Number(settings.z_index)
    };

    console.log('📤 [apiClient] Processed settings to send:', settingsToSend);

    return fetchApi<void>(`/resolution-badge-settings/${userId}`, {
      method: 'POST',
      body: JSON.stringify(settingsToSend),
    });
  },

  isEnabled: async (userId: string = '1'): Promise<boolean> => {
    try {
      console.log('📋 [apiClient] Checking Resolution Badge enabled status...');
      const response = await fetchApi<{ enabled: boolean }>(`/resolution-badge-settings/${userId}/enabled`);
      console.log('📋 [apiClient] Resolution Badge enabled:', response.enabled);
      return response.enabled;
    } catch (error) {
      console.error('❌ [apiClient] Resolution Badge enabled status error:', error);
      return false;
    }
  }
};