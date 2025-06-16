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

  // Helper function to get enable key for a source name
  const getEnableKey = (sourceName: string): string => {
    if (sourceName === 'MyAnimeList') {
      return 'enable_myanimelist';
    }
    return `enable_${sourceName.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '')}`;
  };

  // Helper function to sync review sources with settings
  const syncReviewSourcesWithSettings = (sourcesConfig: any) => {
    console.log("🔄 STARTING SYNC PROCESS");
    console.log("📊 Sources config received:", sourcesConfig);
    console.log("📋 Default review sources:", defaultReviewSources.map(s => ({name: s.source_name, enabled: s.enabled})));
    
    const updatedSources = defaultReviewSources.map(source => {
      const enableKey = getEnableKey(source.source_name);
      const isEnabled = sourcesConfig[enableKey] || false;
      
      console.log(`🔗 Syncing ${source.source_name}:`);
      console.log(`   - Enable key: ${enableKey}`);
      console.log(`   - API value: ${sourcesConfig[enableKey]}`);
      console.log(`   - Converted to: ${isEnabled}`);
      console.log(`   - Original enabled: ${source.enabled}`);
      
      return {
        ...source,
        enabled: isEnabled
      };
    });
    
    console.log("✅ SYNC COMPLETE - Updated sources:");
    updatedSources.forEach(source => {
      console.log(`   ${source.source_name}: ${source.enabled}`);
    });
    
    console.log("🎯 MyAnimeList specifically:", updatedSources.find(s => s.source_name === 'MyAnimeList'));
    
    setReviewSources(updatedSources);
    return updatedSources;
  };

  // Load settings from API
  const loadSettings = async () => {
    setLoading(true);
    
    try {
      console.log('🔄 Loading review settings...');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_review.yml`);
      const data = await response.json();
      
      console.log('📥 Loaded review config:', data);
      
      if (data.config && Object.keys(data.config).length > 0) {
        console.log('📋 Config has data, processing...');
        
        // Deep merge loaded config with defaults to ensure all fields exist
        const mergedSettings = {
          ...defaultReviewSettings,
          ...data.config,
          General: { ...defaultReviewSettings.General, ...data.config.General },
          Sources: { ...defaultReviewSettings.Sources, ...data.config.Sources },
          Text: { ...defaultReviewSettings.Text, ...data.config.Text },
          Background: { ...defaultReviewSettings.Background, ...data.config.Background },
          Border: { ...defaultReviewSettings.Border, ...data.config.Border },
          Shadow: { ...defaultReviewSettings.Shadow, ...data.config.Shadow },
          ImageBadges: { ...defaultReviewSettings.ImageBadges, ...data.config.ImageBadges }
        };
        
        console.log('📦 Merged settings:', mergedSettings);
        console.log('📊 Sources section:', mergedSettings.Sources);
        
        setSettings(mergedSettings);
        
        // CRITICAL FIX: Sync review sources with loaded settings
        if (data.config.Sources) {
          console.log('🔗 Syncing review sources with loaded settings...');
          const syncedSources = syncReviewSourcesWithSettings(data.config.Sources);
          console.log('✅ Review sources synced:', syncedSources.filter(s => s.enabled).map(s => s.source_name));
        } else {
          console.log('⚠️ No Sources config found, using defaults');
          setReviewSources(defaultReviewSources);
        }
        
        console.log('✅ Review settings loaded successfully');
      } else {
        console.log('📭 No existing review config found, using defaults');
        setSettings(defaultReviewSettings);
        setReviewSources(defaultReviewSources);
      }
    } catch (error) {
      console.error('❌ Error loading review settings:', error);
      toast.error('Failed to load review badge settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
      setSettings(defaultReviewSettings);
      setReviewSources(defaultReviewSources);
    } finally {
      setLoading(false);
    }
  };

  // Load review sources (placeholder - these would come from a separate API)
  const loadReviewSources = async () => {
    try {
      console.log('📋 Loading review sources...');
      // For now, use default sources. In the future, this would be an API call
      // NOTE: Don't overwrite reviewSources here if they were already synced in loadSettings
      if (reviewSources === defaultReviewSources) {
        console.log('📋 Setting default review sources');
        setReviewSources(defaultReviewSources);
      } else {
        console.log('📋 Review sources already synced, keeping current state');
      }
      setReviewSourceSettings(defaultReviewSourceSettings);
    } catch (error) {
      console.error('❌ Error loading review sources:', error);
      if (reviewSources === defaultReviewSources) {
        setReviewSources(defaultReviewSources);
      }
      setReviewSourceSettings(defaultReviewSourceSettings);
    }
  };

  // Load available fonts (placeholder)
  const loadFonts = async () => {
    try {
      console.log('🔤 Loading available fonts...');
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
      console.error('❌ Error loading fonts:', error);
      setAvailableFonts([]);
    }
  };

  // Save settings to API
  const saveSettings = async () => {
    setSaving(true);
    
    try {
      console.log('💾 Preparing to save review settings...');
      
      // CRITICAL FIX: Sync all reviewSources state to settings.Sources before saving
      const syncedSources = { ...settings.Sources };
      reviewSources.forEach(source => {
        const enableKey = getEnableKey(source.source_name);
        syncedSources[enableKey] = source.enabled;
        console.log(`💾 Syncing for save: ${source.source_name} -> ${enableKey} = ${source.enabled}`);
      });
      
      const settingsToSave = {
        ...settings,
        Sources: syncedSources
      };
      
      console.log('💾 Saving review settings:', settingsToSave);
      console.log('💾 Sources being saved:', syncedSources);
      console.log('💾 MyAnimeList save value:', syncedSources.enable_myanimelist);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_review.yml`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settingsToSave),
      });

      console.log('💾 Save response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.text();
        console.error('❌ Save failed with response:', errorData);
        throw new Error(`Failed to save settings: ${response.status}`);
      }

      const result = await response.json();
      console.log('✅ Save successful:', result);
      
      // Update local settings state to match what was saved
      setSettings(settingsToSave);
      
      toast.success('Review badge settings saved successfully!', {
        description: 'Your settings have been updated and saved.',
        duration: 3000
      });
    } catch (error) {
      console.error('❌ Error saving review settings:', error);
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
    console.log(`⚙️ Updating setting: ${section}.${key} = ${value}`);
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
    console.log(`🔄 Updating review source: ${updatedSource.source_name} -> enabled: ${updatedSource.enabled}`);
    
    // Update UI state
    setReviewSources(prev => 
      prev.map(source => 
        source.id === updatedSource.id ? updatedSource : source
      )
    );
    
    // CRITICAL FIX: Also update the settings state when a source is toggled
    const enableKey = getEnableKey(updatedSource.source_name);
    
    console.log(`⚙️ Also updating settings: Sources.${enableKey} = ${updatedSource.enabled}`);
    
    setSettings(prev => ({
      ...prev,
      Sources: {
        ...prev.Sources,
        [enableKey]: updatedSource.enabled
      }
    }));
    
    toast.info(`Updated ${updatedSource.source_name}`, {
      duration: 2000
    });
  };

  // Update review source settings
  const updateReviewSourceSettings = (key: keyof ReviewSourceSettings, value: any) => {
    console.log(`⚙️ Updating review source setting: ${key} = ${value}`);
    setReviewSourceSettings(prev => ({
      ...prev,
      [key]: value
    }));
  };

  // Reorder sources
  const reorderSources = (newOrder: ReviewSource[]) => {
    console.log('🔄 Reordering sources:', newOrder.map(s => s.source_name));
    setReviewSources(newOrder);
    toast.success('Source priority updated', {
      duration: 2000
    });
  };

  // Add new image mapping
  const addImageMapping = (rating: string, image: string) => {
    if (rating && image) {
      console.log(`🖼️ Adding image mapping: ${rating} -> ${image}`);
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
    console.log(`🗑️ Removing image mapping: ${rating}`);
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
    
    console.log(`✏️ Updating image name: ${oldName} -> ${newName}`);
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

  // Debug effect to monitor state changes
  useEffect(() => {
    console.log("🔍 STATE CHANGE DETECTED:");
    console.log("   📊 settings.Sources:", settings.Sources);
    console.log("   📋 reviewSources enabled:", reviewSources.filter(s => s.enabled).map(s => s.source_name));
    console.log("   🎯 MyAnimeList in settings:", settings.Sources?.enable_myanimelist);
    console.log("   🎯 MyAnimeList in sources:", reviewSources.find(s => s.source_name === 'MyAnimeList')?.enabled);
  }, [settings.Sources, reviewSources]);

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
