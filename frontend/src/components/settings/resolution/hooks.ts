import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { saveSettingsWithCacheClear } from '@/lib/settings-utils';
import { loadAvailableFonts } from '@/lib/font-utils';
import { ResolutionSettings, defaultResolutionSettings } from './types';

export function useResolutionSettings() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<ResolutionSettings>(defaultResolutionSettings);
  const [availableFonts, setAvailableFonts] = useState<string[]>([]);

  // Load available fonts
  const loadFonts = async () => {
    try {
      console.log('Loading available fonts...');
      const fonts = await loadAvailableFonts();
      setAvailableFonts(fonts);
    } catch (error) {
      console.error('Error loading fonts:', error);
      setAvailableFonts([]);
    }
  };

  // Load settings from API
  const loadSettings = async () => {
    setLoading(true);
    
    try {
      console.log('Loading resolution settings...');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_resolution.yml`);
      const data = await response.json();
      
      console.log('Loaded resolution config:', data);
      
      if (data.config && Object.keys(data.config).length > 0) {
        // Merge loaded config with defaults to ensure all fields exist
        const mergedSettings = {
          ...defaultResolutionSettings,
          ...data.config,
          General: { ...defaultResolutionSettings.General, ...data.config.General },
          Text: { ...defaultResolutionSettings.Text, ...data.config.Text },
          Background: { ...defaultResolutionSettings.Background, ...data.config.Background },
          Border: { ...defaultResolutionSettings.Border, ...data.config.Border },
          Shadow: { ...defaultResolutionSettings.Shadow, ...data.config.Shadow },
          ImageBadges: { ...defaultResolutionSettings.ImageBadges, ...data.config.ImageBadges },
          enhanced_detection: { ...defaultResolutionSettings.enhanced_detection, ...data.config.enhanced_detection },
          performance: { ...defaultResolutionSettings.performance, ...data.config.performance }
        };
        setSettings(mergedSettings);
        console.log('Settings loaded successfully');
      } else {
        console.log('No existing config found, using defaults');
        setSettings(defaultResolutionSettings);
      }
    } catch (error) {
      console.error('Error loading resolution settings:', error);
      toast.error('Failed to load resolution badge settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
      setSettings(defaultResolutionSettings);
    } finally {
      setLoading(false);
    }
  };

  // Save settings to API
  const saveSettings = async () => {
    setSaving(true);
    
    try {
      console.log('Saving resolution settings:', settings);
      
      await saveSettingsWithCacheClear('badge_settings_resolution.yml', settings);
      
      console.log('Save successful');
      
      toast.success('Resolution badge settings saved successfully!', {
        description: 'Your settings have been updated and saved.',
        duration: 3000
      });
    } catch (error) {
      console.error('Error saving resolution settings:', error);
      toast.error('Failed to save resolution badge settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
    } finally {
      setSaving(false);
    }
  };

  // Update a nested setting value
  const updateSetting = (section: keyof ResolutionSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  // Add new resolution mapping
  const addResolutionMapping = (resolution: string, image: string) => {
    if (resolution && image) {
      setSettings(prev => ({
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: {
            ...prev.ImageBadges.image_mapping,
            [resolution]: image
          }
        }
      }));
      
      toast.success(`Added resolution mapping: ${resolution} → ${image}`, {
        duration: 2000
      });
    }
  };

  // Remove resolution mapping
  const removeResolutionMapping = (resolution: string) => {
    setSettings(prev => {
      const newImageMapping = { ...prev.ImageBadges.image_mapping };
      delete newImageMapping[resolution];
      return {
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: newImageMapping
        }
      };
    });
    
    toast.info(`Removed resolution mapping: ${resolution}`, {
      duration: 2000
    });
  };

  // Update resolution name in mapping
  const updateResolutionName = (oldName: string, newName: string) => {
    if (oldName === newName || !newName.trim()) return;
    
    setSettings(prev => {
      const oldValue = prev.ImageBadges.image_mapping[oldName];
      const newImageMapping = { ...prev.ImageBadges.image_mapping };
      delete newImageMapping[oldName];
      newImageMapping[newName] = oldValue;
      
      return {
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: newImageMapping
        }
      };
    });
  };

  // Diagnostic API functions
  const runImageCoverageAnalysis = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings/resolution/coverage`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Image coverage analysis failed:', error);
      throw error;
    }
  };

  const getCacheStats = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings/resolution/cache/stats`);
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Cache stats retrieval failed:', error);
      throw error;
    }
  };

  const clearResolutionCache = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings/resolution/cache`, {
        method: 'DELETE'
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Cache clear failed:', error);
      throw error;
    }
  };

  const testEnhancedDetection = async () => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings/resolution/test`, {
        method: 'POST'
      });
      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Detection test failed:', error);
      throw error;
    }
  };

  return {
    loading,
    saving,
    settings,
    availableFonts,
    loadSettings,
    loadFonts,
    saveSettings,
    updateSetting,
    addResolutionMapping,
    removeResolutionMapping,
    updateResolutionName,
    // Diagnostic functions
    runImageCoverageAnalysis,
    getCacheStats,
    clearResolutionCache,
    testEnhancedDetection
  };
}
