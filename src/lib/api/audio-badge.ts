import { fetchApi, ApiError } from '../api-client';

const DEFAULT_USER_ID = '1'; // Assuming this is still relevant here

export const audioBadge = {
  getSettings: async (): Promise<any> => {
    try {
      console.log('🔧 [apiClient] Fetching Audio Badge settings...');
      const data = await fetchApi<any>(`/audio-badge-settings/${DEFAULT_USER_ID}`);
      console.log('🔧 [apiClient] Received Audio Badge settings:', data);
      return data;
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        console.log('❗ No Audio Badge settings found, using defaults');
        return {
          size: 100,
          margin: 10,
          position: 'top-right',
          audio_codec_type: 'dolby_atmos',
          background_color: '#000000',
          background_transparency: 0.8,
          border_radius: 4,
          border_width: 1,
          border_color: '#ffffff',
          border_transparency: 0.8,
          shadow_toggle: false,
          shadow_color: '#000000',
          shadow_blur_radius: 5,
          shadow_offset_x: 2,
          shadow_offset_y: 2,
          z_index: 1
        };
      }
      console.error('❌ [apiClient] Audio Badge settings error:', error);
      throw error;
    }
  },

  saveSettings: async (settings: any): Promise<void> => {
    console.log('📤 [apiClient] Saving Audio Badge settings:', settings);

    const requiredFields = [
      'size',
      'margin',
      'position',
      'audio_codec_type',
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
      audio_codec_type: String(settings.audio_codec_type),
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

    return fetchApi<void>(`/audio-badge-settings/${DEFAULT_USER_ID}`, {
      method: 'POST',
      body: JSON.stringify(settingsToSend),
    });
  }
};