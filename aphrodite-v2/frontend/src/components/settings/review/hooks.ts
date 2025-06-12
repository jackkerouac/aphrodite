import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { ReviewSettings, ReviewSource, ReviewSourceSettings, defaultReviewSettings, defaultReviewSourceSettings, defaultReviewSources } from './types';

export function useReviewSettings() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<ReviewSettings>(defaultReviewSettings);
  const [reviewSources, setReviewSources] = useState<ReviewSource[]>(defaultReviewSources);
  const [reviewSourceSettings, setReviewSourceSettings] = useState<ReviewSourceSettings>(defaultReviewSourceSettings);
  const [availableFonts, setAvailableFonts] = useState<string[]>([]);

  // Load settings from API
  const loadSettings = async () => {
    setLoading(true);
    
    try {
      console.log('Loading review settings...');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_review.yml`);
      const data = await response.json();
      
      console.log('Loaded review config:', data);
      
      if (data.config && Object.keys(data.config).length > 0) {
        // Deep merge loaded config with defaults to ensure all fields exist
        const mergedSettings = {
          ...defaultReviewSettings,
          ...data.config,
          General: { ...defaultReviewSettings.General, ...data.config.General },
          Text: { ...defaultReviewSettings.Text, ...data.config.Text },
          Background: { ...defaultReviewSettings.Background, ...data.config.Background },
          Border: { ...defaultReviewSettings.Border, ...data.config.Border },
          Shadow: { ...defaultReviewSettings.Shadow, ...data.config.Shadow },
          ImageBadges: { ...defaultReviewSettings.ImageBadges, ...data.config.ImageBadges }
        };
        setSettings(mergedSettings);
        console.log('Review settings loaded successfully');
      } else {
        console.log('No existing review config found, using defaults');
        setSettings(defaultReviewSettings);
      }
    } catch (error) {
      console.error('Error loading review settings:', error);
      toast.error('Failed to load review badge settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
      setSettings(defaultReviewSettings);
    } finally {
      setLoading(false);
    }
  };

  // Load review sources (placeholder - these would come from a separate API)
  const loadReviewSources = async () => {
    try {
      console.log('Loading review sources...');
      // For now, use default sources. In the future, this would be an API call
      setReviewSources(defaultReviewSources);
      setReviewSourceSettings(defaultReviewSourceSettings);
    } catch (error) {
      console.error('Error loading review sources:', error);
      setReviewSources(defaultReviewSources);
      setReviewSourceSettings(defaultReviewSourceSettings);
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
      console.log('Saving review settings:', settings);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_review.yml`, {
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
      
      toast.success('Review badge settings saved successfully!', {
        description: 'Your settings have been updated and saved.',
        duration: 3000
      });
    } catch (error) {
      console.error('Error saving review settings:', error);
      toast.error('Failed to save review badge settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
    } finally {
      setSaving(false);
    }
  };

  // Update a nested setting value
  const updateSetting = (section: keyof ReviewSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value
      }
    }));
  };

  // Update review source
  const updateReviewSource = (updatedSource: ReviewSource) => {
    setReviewSources(prev => 
      prev.map(source => 
        source.id === updatedSource.id ? updatedSource : source
      )
    );
    
    toast.info(`Updated ${updatedSource.source_name}`, {
      duration: 2000
    });
  };

  // Update review source settings
  const updateReviewSourceSettings = (key: keyof ReviewSourceSettings, value: any) => {
    setReviewSourceSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Reorder sources
  const reorderSources = (newOrder: ReviewSource[]) => {
    setReviewSources(newOrder);
    toast.success('Source priority updated', {
      duration: 2000
    });
  };

  // Add new image mapping
  const addImageMapping = (rating: string, image: string) => {
    if (rating && image) {
      setSettings(prev => ({
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: {
            ...prev.ImageBadges.image_mapping,
            [rating]: image
          }
        }
      }));
      
      toast.success(`Added image mapping: ${rating} → ${image}`, {
        duration: 2000
      });
    }
  };

  // Remove image mapping
  const removeImageMapping = (rating: string) => {
    setSettings(prev => {
      const newImageMapping = { ...prev.ImageBadges.image_mapping };
      delete newImageMapping[rating];
      return {
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: newImageMapping
        }
      };
    });
    
    toast.info(`Removed image mapping: ${rating}`, {
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

  return {
    loading,
    saving,
    settings,
    reviewSources,
    reviewSourceSettings,
    availableFonts,
    loadSettings,
    loadReviewSources,
    loadFonts,
    saveSettings,
    updateSetting,
    updateReviewSource,
    updateReviewSourceSettings,
    reorderSources,
    addImageMapping,
    removeImageMapping,
    updateImageName
  };
}
