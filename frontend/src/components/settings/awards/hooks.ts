import { useState } from 'react';
import { toast } from 'sonner';
import { AwardsSettings, defaultAwardsSettings } from './types';

export function useAwardsSettings() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<AwardsSettings>(defaultAwardsSettings);
  const [availableFonts, setAvailableFonts] = useState<string[]>([]);

  // Load settings from API
  const loadSettings = async () => {
    setLoading(true);
    
    try {
      console.log('Loading awards settings...');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_awards.yml`);
      const data = await response.json();
      
      console.log('Loaded awards config:', data);
      
      if (data.config && Object.keys(data.config).length > 0) {
        // Deep merge loaded config with defaults to ensure all fields exist
        const mergedSettings = {
          ...defaultAwardsSettings,
          ...data.config,
          General: { ...defaultAwardsSettings.General, ...data.config.General },
          Awards: { ...defaultAwardsSettings.Awards, ...data.config.Awards },
          Text: { ...defaultAwardsSettings.Text, ...data.config.Text },
          Background: { ...defaultAwardsSettings.Background, ...data.config.Background },
          Border: { ...defaultAwardsSettings.Border, ...data.config.Border },
          Shadow: { ...defaultAwardsSettings.Shadow, ...data.config.Shadow },
          ImageBadges: { ...defaultAwardsSettings.ImageBadges, ...data.config.ImageBadges }
        };
        setSettings(mergedSettings);
        console.log('Awards settings loaded successfully');
      } else {
        console.log('No existing awards config found, using defaults');
        setSettings(defaultAwardsSettings);
      }
    } catch (error) {
      console.error('Error loading awards settings:', error);
      toast.error('Failed to load awards badge settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
      setSettings(defaultAwardsSettings);
    } finally {
      setLoading(false);
    }
  };

  // Load available fonts (placeholder)
  const loadFonts = async () => {
    try {
      console.log('Loading available fonts...');
      // For now, use default fonts. In the future, this would be an API call
      setAvailableFonts([
        'AvenirNextLTProBold.otf',
        'DejaVuSans.ttf',
        'Arial',
        'Helvetica',
        'Times New Roman',
        'Courier New'
      ]);
    } catch (error) {
      console.error('Error loading fonts:', error);
      setAvailableFonts([]);
    }
  };

  // Save settings to API
  const saveSettings = async () => {
    setSaving(true);
    
    try {
      console.log('Saving awards settings:', settings);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_awards.yml`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      console.log('Save response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.text();
        console.error('Save failed with response:', errorData);
        throw new Error(`Failed to save settings: ${response.status}`);
      }

      const result = await response.json();
      console.log('Save successful:', result);
      
      toast.success('Awards badge settings saved successfully!', {
        description: 'Your settings have been updated and saved.',
        duration: 3000
      });
    } catch (error) {
      console.error('Error saving awards settings:', error);
      toast.error('Failed to save awards badge settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
    } finally {
      setSaving(false);
    }
  };

  // Update a nested setting value
  const updateSetting = (section: keyof AwardsSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  // Add new image mapping
  const addImageMapping = (award: string, image: string) => {
    if (award && image) {
      setSettings(prev => ({
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: {
            ...prev.ImageBadges.image_mapping,
            [award]: image
          }
        }
      }));
      
      toast.success(`Added image mapping: ${award} → ${image}`, {
        duration: 2000
      });
    }
  };

  // Remove image mapping
  const removeImageMapping = (award: string) => {
    setSettings(prev => {
      const newImageMapping = { ...prev.ImageBadges.image_mapping };
      delete newImageMapping[award];
      return {
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: newImageMapping
        }
      };
    });
    
    toast.info(`Removed image mapping: ${award}`, {
      duration: 2000
    });
  };

  // Update image name in mapping
  const updateImageName = (oldName: string, newName: string) => {
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

  // Update award sources array
  const updateAwardSources = (sources: string[]) => {
    setSettings(prev => ({
      ...prev,
      Awards: {
        ...prev.Awards,
        award_sources: sources
      }
    }));
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
    addImageMapping,
    removeImageMapping,
    updateImageName,
    updateAwardSources
  };
}
