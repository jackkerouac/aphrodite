import { useState, useEffect, useCallback } from 'react';
import { toast } from 'sonner';
import apiClient, { ApiError } from '@/lib/api-client';

interface ResolutionBadgeSettings {
  size: number | null;
  margin: number | null;
  background_color: string;
  background_transparency: number | null;
  border_radius: number | null;
  border_width: number | null;
  border_color: string;
  border_transparency: number | null;
  shadow_toggle: boolean;
  shadow_color: string;
  shadow_blur_radius: number | null;
  shadow_offset_x: number | null;
  shadow_offset_y: number | null;
  z_index: number | null;
}

export interface UseResolutionBadgeSettingsReturn {
  settings: ResolutionBadgeSettings;
  loading: boolean;
  error: Error | null;
  saving: boolean;
  fetchSettings: () => Promise<void>;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleColorChange: (colorType: 'background' | 'border' | 'shadow', color: string) => void;
  handleToggleChange: (fieldName: string, checked: boolean) => void;
  handleSave: () => Promise<void>;
  isSaveDisabled: boolean;
}

const defaultSettings: ResolutionBadgeSettings = {
  size: 0.1, // 10% of poster size
  margin: 10,
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

export const useResolutionBadgeSettings = (userId: number = 1): UseResolutionBadgeSettingsReturn => {
  console.log('[useResolutionBadgeSettings] Initializing hook for user:', userId);
  
  const [settings, setSettings] = useState<ResolutionBadgeSettings>(defaultSettings);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [saving, setSaving] = useState(false);

  // Fetch settings from the API
  const fetchSettings = useCallback(async () => {
    try {
      console.log(`[useResolutionBadgeSettings] Fetching settings for user: ${userId}`);
      setLoading(true);
      setError(null);
      
      const data = await apiClient.resolutionBadge.getSettings();
      console.log('[useResolutionBadgeSettings] Received settings:', data);
      
      // Convert string values to appropriate types for form fields
      const formattedSettings = {
        ...data,
        size: data.size,
        margin: data.margin,
        background_transparency: data.background_transparency,
        border_radius: data.border_radius,
        border_width: data.border_width,
        border_transparency: data.border_transparency,
        shadow_toggle: Boolean(data.shadow_toggle),
        shadow_blur_radius: data.shadow_blur_radius,
        shadow_offset_x: data.shadow_offset_x,
        shadow_offset_y: data.shadow_offset_y,
        z_index: data.z_index
      };
      
      setSettings(formattedSettings);
    } catch (error) {
      console.error('[useResolutionBadgeSettings] Error fetching settings:', error);
      setError(error as Error);
      
      // Only show toast if it's not a 404 (not found) error
      if (!(error instanceof ApiError && error.status === 404)) {
        toast.error('Failed to load resolution badge settings');
      }
    } finally {
      setLoading(false);
    }
  }, [userId]);

  // Handle input changes
  const handleChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type, checked } = e.target;
    console.log(`[useResolutionBadgeSettings] Input changed: ${name} = ${type === 'checkbox' ? checked : value}`);
    
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : 
              type === 'number' ? value === '' ? null : Number(value) : 
              value
    }));
  }, []);

  // Handle color picker changes
  const handleColorChange = useCallback((colorType: 'background' | 'border' | 'shadow', color: string) => {
    console.log(`[useResolutionBadgeSettings] Color changed: ${colorType} = ${color}`);
    
    setSettings(prev => {
      if (colorType === 'background') {
        return {
          ...prev,
          background_color: color
        };
      } else if (colorType === 'border') {
        return {
          ...prev,
          border_color: color
        };
      } else if (colorType === 'shadow') {
        return {
          ...prev,
          shadow_color: color
        };
      }
      return prev;
    });
  }, []);

  // Handle toggle changes (like switch components)
  const handleToggleChange = useCallback((fieldName: string, checked: boolean) => {
    console.log(`[useResolutionBadgeSettings] Toggle changed: ${fieldName} = ${checked}`);
    
    setSettings(prev => ({
      ...prev,
      [fieldName]: checked
    }));
  }, []);

  // Save settings to the API
  const handleSave = useCallback(async () => {
    try {
      console.log('[useResolutionBadgeSettings] Saving settings:', settings);
      setSaving(true);
      
      await apiClient.resolutionBadge.saveSettings(settings);
      console.log('[useResolutionBadgeSettings] Settings saved successfully');
      
      // Refresh settings to ensure UI is in sync with database
      await fetchSettings();
      
      toast.success('Resolution Badge Settings Saved', {
        description: 'Your resolution badge settings have been successfully updated.',
      });
      return Promise.resolve();
    } catch (error) {
      console.error('[useResolutionBadgeSettings] Error saving settings:', error);
      toast.error('Error Saving Settings', {
        description: error instanceof Error ? error.message : 'An unexpected error occurred.',
      });
      return Promise.reject(error);
    } finally {
      setSaving(false);
    }
  }, [settings, userId, fetchSettings]);

  // Check if required fields are filled
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
  
  // Also check shadow fields if shadow is enabled
  const shadowFields = [
    'shadow_color',
    'shadow_blur_radius',
    'shadow_offset_x',
    'shadow_offset_y'
  ];
  
  const hasEmptyRequiredFields = requiredFields.some(field => 
    settings[field as keyof ResolutionBadgeSettings] === null || 
    settings[field as keyof ResolutionBadgeSettings] === undefined ||
    (typeof settings[field as keyof ResolutionBadgeSettings] === 'string' && 
     (settings[field as keyof ResolutionBadgeSettings] as string).trim() === '')
  );
  
  const hasEmptyShadowFields = settings.shadow_toggle && shadowFields.some(field => 
    settings[field as keyof ResolutionBadgeSettings] === null || 
    settings[field as keyof ResolutionBadgeSettings] === undefined ||
    (typeof settings[field as keyof ResolutionBadgeSettings] === 'string' && 
     (settings[field as keyof ResolutionBadgeSettings] as string).trim() === '')
  );
  
  const isSaveDisabled = hasEmptyRequiredFields || hasEmptyShadowFields;

  // Fetch settings on initial load
  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  return {
    settings,
    loading,
    error,
    saving,
    fetchSettings,
    handleChange,
    handleColorChange,
    handleToggleChange,
    handleSave,
    isSaveDisabled
  };
};
