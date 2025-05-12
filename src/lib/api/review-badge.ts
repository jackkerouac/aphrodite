import { fetchApi, ApiError } from '../api-client';
import { ReviewBadgeSettings } from '@/pages/settings/review-badge/hooks/useReviewBadgeSettings';
import { reviewSources } from '@/pages/settings/review-badge/constants';

export const reviewBadge = {
  getSettings: async (userId: string = '1'): Promise<ReviewBadgeSettings> => {
    try {
      console.log('🔧 [apiClient] Fetching Review Badge settings...');
      const data = await fetchApi<ReviewBadgeSettings>(`/review-badge-settings/${userId}`);
      console.log('🔧 [apiClient] Received Review Badge settings:', data);
      return data;
    } catch (error) {
      if (error instanceof ApiError && error.status === 404) {
        console.log('❗ No Review Badge settings found, using defaults');
        // Return default settings from the hook
        return {
          position: 'top-right',
          badge_layout: 'horizontal',
          display_sources: ['IMDB', 'TMDB'],
          source_order: ['IMDB', 'TMDB', 'RottenTomatoes', 'Metacritic', 'AniDB'],
          show_logo: true,
          logo_size: 24,
          logo_position: 'top',
          logoTextSpacing: 5,
          score_format: 'decimal',
          size: 100,
          margin: 10,
          spacing: 5,
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
          font_family: 'Inter',
          font_size: 16,
          font_weight: 600,
          text_color: '#ffffff',
          text_transparency: 0,
          use_brand_colors: true,
        };
      }
      console.error('❌ [apiClient] Review Badge settings error:', error);
      throw error;
    }
  },

  saveSettings: async (settings: ReviewBadgeSettings, userId: string = '1'): Promise<void> => {
    console.log('📤 [apiClient] Saving Review Badge settings:', settings);

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
        positionValue = 'bottom-left';
      }
    } else {
      positionValue = 'bottom-left';
    }
    
    // Map all properties - handle both camelCase and snake_case inputs
    settingsToSend.size = Number(settings.size);
    settingsToSend.margin = Number(settings.margin);
    settingsToSend.position = positionValue;
    settingsToSend.background_color = String(settings.background_color || settings.backgroundColor || '#000000');
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
    settingsToSend.badge_layout = String(settings.badge_layout || settings.displayFormat || 'horizontal');
    settingsToSend.display_sources = Array.isArray(settings.display_sources) ? settings.display_sources : (Array.isArray(settings.displaySources) ? settings.displaySources : ['IMDB', 'TMDB']);
    settingsToSend.source_order = Array.isArray(settings.source_order) ? settings.source_order : (Array.isArray(settings.sourceOrder) ? settings.sourceOrder : reviewSources);
    settingsToSend.show_logo = Boolean(settings.show_logo || settings.showLogo || true);
    settingsToSend.logo_size = Number(settings.logo_size || settings.logoSize || 24);
    settingsToSend.logo_position = String(settings.logo_position || settings.logoPosition || 'top');
    settingsToSend.logo_text_spacing = Number(settings.logo_text_spacing || settings.logoTextSpacing || 5);
    settingsToSend.score_format = String(settings.score_format || settings.scoreFormat || 'decimal');
    settingsToSend.spacing = Number(settings.spacing || 5);
    settingsToSend.font_family = String(settings.font_family || settings.fontFamily || 'Inter');
    settingsToSend.font_size = Number(settings.font_size || settings.fontSize || 16);
    settingsToSend.font_weight = Number(settings.font_weight || settings.fontWeight || 600);
    settingsToSend.text_color = String(settings.text_color || settings.textColor || '#ffffff');
    settingsToSend.text_opacity = Number(settings.text_opacity || settings.text_transparency || settings.textOpacity || 0);
    settingsToSend.max_sources_to_show = Number(settings.max_sources_to_show || settings.maxSourcesToShow || 3);
    settingsToSend.use_brand_colors = settings.use_brand_colors !== undefined ? Boolean(settings.use_brand_colors) : 
                                    (settings.useBrandColors !== undefined ? Boolean(settings.useBrandColors) : true);
    
    // Check for required fields
    const requiredFields = [
      'size',
      'margin',
      'position',
      'background_color',
      'background_opacity',
      'border_radius',
      'border_width',
      'border_color',
      'border_opacity',
      'z_index'
    ];

    const missingFields: string[] = [];
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

    return fetchApi<void>(`/review-badge-settings/${userId}`, {
      method: 'POST',
      body: JSON.stringify(settingsToSend),
    });
  },

  isEnabled: async (userId: string = '1'): Promise<boolean> => {
    try {
      console.log('📋 [apiClient] Checking Review Badge enabled status...');
      const response = await fetchApi<{ enabled: boolean }>(`/review-badge-settings/${userId}/enabled`);
      console.log('📋 [apiClient] Review Badge enabled:', response.enabled);
      return response.enabled;
    } catch (error) {
      console.error('❌ [apiClient] Review Badge enabled status error:', error);
      return false;
    }
  }
};