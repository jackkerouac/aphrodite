import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { saveSettingsWithCacheClear } from '@/lib/settings-utils';
import { ResolutionSettings, defaultResolutionSettings } from './types';

export function useResolutionSettings() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<ResolutionSettings>(defaultResolutionSettings);

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
          ImageBadges: { ...defaultResolutionSettings.ImageBadges, ...data.config.ImageBadges }
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

  return {
    loading,
    saving,
    settings,
    loadSettings,
    saveSettings,
    updateSetting,
    addResolutionMapping,
    removeResolutionMapping,
    updateResolutionName
  };
}
