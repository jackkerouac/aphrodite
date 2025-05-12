import { fetchApi, ApiError } from '../api-client';

export const audioBadge = {
  getSettings: async (userId: string = '1'): Promise<any> => {
    try {
      console.log('🔧 [apiClient] Fetching Audio Badge settings...');
      const data = await fetchApi<any>(`/audio-badge-settings/${userId}`);
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
          z_index: 1,
          use_brand_colors: true
        };
      }
      console.error('❌ [apiClient] Audio Badge settings error:', error);
      throw error;
    }
  },

  saveSettings: async (settings: any, userId: string = '1'): Promise<void> => {
    console.log('📤 [apiClient] Saving Audio Badge settings:', settings);

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
        positionValue = 'top-left';
      }
    } else {
      positionValue = 'top-left';
    }
    
    // Map all properties - handle both camelCase and snake_case inputs
    settingsToSend.size = parseInt(String(settings.size), 10);  // Force a numeric value
    settingsToSend.margin = Number(settings.margin);
    settingsToSend.position = positionValue;
    settingsToSend.codec_type = String(settings.codec_type || settings.audio_codec_type || settings.codecType || 'Dolby Atmos');
    
    // Handle background color with extra logging
    const sourceBackgroundColor = settings.background_color || settings.backgroundColor;
    console.log('Source background color:', sourceBackgroundColor);
    console.log('background_color property:', settings.background_color);
    console.log('backgroundColor property:', settings.backgroundColor);
    settingsToSend.background_color = String(sourceBackgroundColor || '#000000');
    console.log('Final background_color sent to API:', settingsToSend.background_color);
    settingsToSend.background_opacity = Number(settings.background_opacity || settings.background_transparency || settings.backgroundOpacity || 0.8);
    settingsToSend.border_radius = Number(settings.border_radius || settings.borderRadius || 4);
    settingsToSend.border_width = Number(settings.border_width || settings.borderWidth || 1);
    settingsToSend.border_color = String(settings.border_color || settings.borderColor || '#ffffff');
    settingsToSend.border_opacity = Number(settings.border_opacity || settings.border_transparency || settings.borderOpacity || 0.8);
    settingsToSend.shadow_enabled = Boolean(settings.shadow_enabled || settings.shadow_toggle || settings.shadowEnabled || false);
    settingsToSend.shadow_color = String(settings.shadow_color || settings.shadowColor || '#000000');
    settingsToSend.shadow_blur = Number(settings.shadow_blur || settings.shadow_blur_radius || settings.shadowBlur || 5);
    settingsToSend.shadow_offset_x = Number(settings.shadow_offset_x || settings.shadowOffsetX || 2);
    settingsToSend.shadow_offset_y = Number(settings.shadow_offset_y || settings.shadowOffsetY || 2);
    settingsToSend.z_index = Number(settings.z_index || settings.zIndex || 1);
    settingsToSend.badge_image = settings.badge_image || null;
    settingsToSend.text_color = String(settings.text_color || settings.textColor || '#FFFFFF');
    settingsToSend.font_family = String(settings.font_family || settings.fontFamily || 'Arial');
    settingsToSend.font_size = Number(settings.font_size || settings.fontSize || 24);
    settingsToSend.use_brand_colors = settings.use_brand_colors !== undefined ? Boolean(settings.use_brand_colors) : 
                                    (settings.useBrandColors !== undefined ? Boolean(settings.useBrandColors) : true);
    
    // Check for required fields
    const requiredFields = [
      'size',
      'margin',
      'position',
      'codec_type',
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

    // Final check for required fields and ensure none are null or undefined
    const criticalFields = ['size', 'position', 'codec_type', 'shadow_enabled', 'shadow_color'];
    
    criticalFields.forEach(field => {
      if (settingsToSend[field] === undefined || settingsToSend[field] === null) {
        console.warn(`Critical field ${field} is ${settingsToSend[field] === undefined ? 'undefined' : 'null'}, setting default value`);
        
        // Set default values based on field type
        switch (field) {
          case 'shadow_enabled':
            settingsToSend[field] = false;
            break;
          case 'shadow_color':
            settingsToSend[field] = '#000000';
            break;
          case 'position':
            settingsToSend[field] = 'top-left';
            break;
          case 'codec_type':
            settingsToSend[field] = 'Dolby Atmos';
            break;
          case 'size':
            settingsToSend[field] = 100; // Default size
            break;
        }
      }
    });
    
    console.log('Detailed settings being sent to API:');
    console.log(`  - size: ${settingsToSend.size} (${typeof settingsToSend.size})`);
    console.log(`  - margin: ${settingsToSend.margin} (${typeof settingsToSend.margin})`);
    console.log(`  - position: ${settingsToSend.position} (${typeof settingsToSend.position})`);
    console.log(`  - codec_type: ${settingsToSend.codec_type}`);
    console.log(`  - background_opacity: ${settingsToSend.background_opacity} (${typeof settingsToSend.background_opacity})`);
    console.log(`  - border_radius: ${settingsToSend.border_radius} (${typeof settingsToSend.border_radius})`);
    
    console.log('📤 [apiClient] Processed settings to send:');
    console.log('  - Has badge_image:', !!settingsToSend.badge_image);
    console.log('  - Badge image length:', settingsToSend.badge_image ? settingsToSend.badge_image.length : 0);
    console.log('  - Use brand colors:', settingsToSend.use_brand_colors);

    return fetchApi<void>(`/audio-badge-settings/${userId}`, {
      method: 'POST',
      body: JSON.stringify(settingsToSend),
    });
  },

  isEnabled: async (userId: string = '1'): Promise<boolean> => {
    try {
      console.log('📋 [apiClient] Checking Audio Badge enabled status...');
      const response = await fetchApi<{ enabled: boolean }>(`/audio-badge-settings/${userId}/enabled`);
      console.log('📋 [apiClient] Audio Badge enabled:', response.enabled);
      return response.enabled;
    } catch (error) {
      console.error('❌ [apiClient] Audio Badge enabled status error:', error);
      return false;
    }
  }
};