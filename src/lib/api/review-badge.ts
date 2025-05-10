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
        };
      }
      console.error('❌ [apiClient] Review Badge settings error:', error);
      throw error;
    }
  },

  saveSettings: async (settings: ReviewBadgeSettings, userId: string = '1'): Promise<void> => {
    console.log('📤 [apiClient] Saving Review Badge settings:', settings);

    const requiredFields = [
      'size',
      'margin',
      'background_color',
      'background_transparency',
      'border_radius',
      'border_width',
      'border_color',
      'border_transparency',
      'z_index'
    ];

    const missingFields: string[] = [];
    for (const field of requiredFields) {
      const value = settings[field as keyof ReviewBadgeSettings];
      if (value === undefined || value === null || value === '') {
        missingFields.push(field);
      }
    }

    if (missingFields.length > 0) {
      console.error('🚫 [apiClient] Missing required fields:', missingFields);
      console.error('🚫 [apiClient] Current settings values:', settings);
      throw new Error(`Missing required fields: ${missingFields.join(', ')}`);
    }

    // Include all fields for the backend
    const settingsToSend = {
      size: Number(settings.size),
      margin: Number(settings.margin),
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
      z_index: Number(settings.z_index),
      position: String(settings.position),
      badge_layout: String(settings.badge_layout),
      // Convert the arrays to proper PostgreSQL array format
      display_sources: Array.isArray(settings.display_sources) ? settings.display_sources : [],
      source_order: Array.isArray(settings.source_order) ? settings.source_order : reviewSources,
      show_logo: Boolean(settings.show_logo),
      logo_size: Number(settings.logo_size),
      logo_position: String(settings.logo_position),
      logo_text_spacing: Number(settings.logoTextSpacing),
      score_format: String(settings.score_format),
      spacing: Number(settings.spacing),
      font_family: String(settings.font_family),
      font_size: Number(settings.font_size),
      font_weight: Number(settings.font_weight),
      text_color: String(settings.text_color),
      text_transparency: Number(settings.text_transparency)
    };

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