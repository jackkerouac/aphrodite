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
          z_index: 10,
          use_brand_colors: true
        };
      }
      console.error('❌ [apiClient] Resolution Badge settings error:', error);
      throw error;
    }
  },

  saveSettings: async (settings: any, userId: string = '1'): Promise<void> => {
    console.log('📤 [apiClient] Saving Resolution Badge settings:', settings);
    
    // Convert camelCase to snake_case and ensure all required fields are properly mapped
    const settingsToSend: any = {};
    
    // Handle position - could be enum or string format
    let positionValue;
    if (settings.position) {
      if (typeof settings.position === 'string') {
        // The position may be in formats like 'TopRight', 'top-right', etc.
        // Normalize to the format expected by the backend ('top-right')
        positionValue = settings.position
          .replace(/([A-Z])/g, '-$1')
          .toLowerCase()
          .replace(/^-/, '');
      } else if (typeof settings.position === 'object' && settings.position.name) {
        // Handle enum objects like BadgePosition.TopRight
        positionValue = settings.position.name
          .replace(/([A-Z])/g, '-$1')
          .toLowerCase()
          .replace(/^-/, '');
      } else {
        // Default fallback
        positionValue = 'top-right';
      }
    } else {
      positionValue = 'top-right';
    }
    
    // Map all properties - handle both camelCase and snake_case inputs
    settingsToSend.size = Number(settings.size || settings.size);
    settingsToSend.margin = Number(settings.margin || settings.margin);
    settingsToSend.position = positionValue;
    settingsToSend.resolution_type = String(settings.resolution_type || settings.resolutionType || '1080p');
    settingsToSend.background_color = String(settings.background_color || settings.backgroundColor || '#000000');
    settingsToSend.background_opacity = Number(settings.background_opacity || settings.background_transparency || settings.backgroundOpacity || 0.7);
    settingsToSend.border_radius = Number(settings.border_radius || settings.borderRadius || 5);
    settingsToSend.border_width = Number(settings.border_width || settings.borderWidth || 1);
    settingsToSend.border_color = String(settings.border_color || settings.borderColor || '#000000');
    settingsToSend.border_opacity = Number(settings.border_opacity || settings.border_transparency || settings.borderOpacity || 0.9);
    settingsToSend.shadow_enabled = Boolean(settings.shadow_enabled || settings.shadow_toggle || settings.shadowEnabled || false);
    settingsToSend.shadow_color = String(settings.shadow_color || settings.shadowColor || '#000000');
    settingsToSend.shadow_blur = Number(settings.shadow_blur || settings.shadow_blur_radius || settings.shadowBlur || 5);
    settingsToSend.shadow_offset_x = Number(settings.shadow_offset_x || settings.shadowOffsetX || 0);
    settingsToSend.shadow_offset_y = Number(settings.shadow_offset_y || settings.shadowOffsetY || 0);
    settingsToSend.z_index = Number(settings.z_index || settings.zIndex || 10);
    settingsToSend.use_brand_colors = settings.use_brand_colors !== undefined ? Boolean(settings.use_brand_colors) : 
                                    (settings.useBrandColors !== undefined ? Boolean(settings.useBrandColors) : false);
    
    // Check for required fields
    const requiredFields = [
      'size',
      'margin',
      'position',
      'resolution_type',
      'background_color',
      'background_opacity',
      'border_radius',
      'border_width',
      'border_color',
      'border_opacity',
      'z_index'
    ];

    const missingFields = [];
    for (const field of requiredFields) {
      if (settingsToSend[field] === undefined || settingsToSend[field] === null || settingsToSend[field] === '') {
        missingFields.push(field);
      }
    }

    if (missingFields.length > 0) {
      console.error('🚫 [apiClient] Missing required fields:', missingFields);
      console.error('🚫 [apiClient] Current settings values:', settingsToSend);
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }

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