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
          Sources: { ...defaultReviewSettings.Sources, ...data.config.Sources },
          Text: { ...defaultReviewSettings.Text, ...data.config.Text },
          Background: { ...defaultReviewSettings.Background, ...data.config.Background },
          Border: { ...defaultReviewSettings.Border, ...data.config.Border },
          Shadow: { ...defaultReviewSettings.Shadow, ...data.config.Shadow },
          ImageBadges: { ...defaultReviewSettings.ImageBadges, ...data.config.ImageBadges }
        };
        setSettings(mergedSettings);
        
        // CRITICAL FIX: Sync review sources with loaded settings
        if (data.config.Sources) {
          console.log('🔄 Starting reviewSources sync with API data...');
          console.log('📊 API Sources config:', data.config.Sources);
          console.log('📋 Default sources before sync:', defaultReviewSources.map(s => ({name: s.source_name, enabled: s.enabled, priority: s.priority})));
          
          // Get saved priority order from API
          const savedPriorityOrder = data.config.Sources.source_priority || defaultReviewSettings.Sources.source_priority;
          console.log('📌 Saved priority order:', savedPriorityOrder);
          
          let updatedSources = defaultReviewSources.map(source => {
            // Map source names to enable settings - handle the specific naming conversion
            let enableKey = '';
            if (source.source_name === 'MyAnimeList') {
              enableKey = 'enable_myanimelist';
            } else {
              enableKey = `enable_${source.source_name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '')}`;
            }
            
            const isEnabled = data.config.Sources[enableKey] || false;
            
            console.log(`🔗 Syncing ${source.source_name}: ${enableKey} = ${isEnabled} (API: ${data.config.Sources[enableKey]}) - Original priority: ${source.priority}`);
            
            // ONLY sync enabled state, preserve original priority/order for now
            return {
              ...source,
              enabled: isEnabled
            };
          });
          
          // Apply saved priority order
          updatedSources = updatedSources.map(source => {
            // Find this source in the saved priority order
            const sourceLookupName = source.source_name === 'MyAnimeList' ? 'myanimelist' :
                                   source.source_name === 'IMDb' ? 'imdb' :
                                   source.source_name === 'Rotten Tomatoes Critics' ? 'rotten_tomatoes' :
                                   source.source_name === 'Rotten Tomatoes Audience' ? 'rotten_tomatoes_audience' :
                                   source.source_name === 'Metacritic' ? 'metacritic' :
                                   source.source_name === 'TMDb' ? 'tmdb' :
                                   source.source_name === 'AniDB' ? 'anidb' :
                                   source.source_name === 'Letterboxd' ? 'letterboxd' :
                                   source.source_name === 'Trakt' ? 'trakt' :
                                   source.source_name === 'MDBList' ? 'mdblist' :
                                   source.source_name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
            
            const priorityIndex = savedPriorityOrder.findIndex(p => p === sourceLookupName);
            const newPriority = priorityIndex !== -1 ? priorityIndex + 1 : source.priority;
            
            console.log(`📌 ${source.source_name}: ${sourceLookupName} found at index ${priorityIndex} -> priority ${source.priority} -> ${newPriority}`);
            
            return {
              ...source,
              priority: newPriority,
              display_order: newPriority
            };
          });
          
          console.log('📋 Updated sources after sync:', updatedSources.map(s => ({name: s.source_name, enabled: s.enabled, priority: s.priority})));
          console.log('🎯 MyAnimeList specifically:', updatedSources.find(s => s.source_name === 'MyAnimeList'));
          
          setReviewSources(updatedSources);
          console.log('✅ Review sources synced with settings - Enabled sources:', updatedSources.filter(s => s.enabled).map(s => s.source_name));
        } else {
          console.log('⚠️ No Sources config in API data, keeping defaults');
        }
        
        console.log('✅ Review settings loaded successfully');
        console.log('📊 Final settings state:', mergedSettings.Sources);
        console.log('📋 Final reviewSources state will be set by sync above');
        
        // Load review source settings separately
        await loadReviewSourceSettings();
      } else {
        console.log('No existing review config found, using defaults');
        setSettings(defaultReviewSettings);
        setReviewSources(defaultReviewSources);
        setReviewSourceSettings(defaultReviewSourceSettings);
      }
    } catch (error) {
      console.error('Error loading review settings:', error);
      toast.error('Failed to load review badge settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 5000
      });
      setSettings(defaultReviewSettings);
      setReviewSources(defaultReviewSources);
      setReviewSourceSettings(defaultReviewSourceSettings);
    } finally {
      setLoading(false);
    }
  };

  // Load review sources (placeholder - these would come from a separate API)
  const loadReviewSources = async () => {
    try {
      console.log('Loading review sources...');
      console.log('Current reviewSources state:', reviewSources.map(s => ({name: s.source_name, enabled: s.enabled})));
      
      // CRITICAL FIX: Only set defaults if reviewSources haven't been synced from settings yet
      // Check if any sources have been enabled (which would indicate sync happened)
      const hasSyncedData = reviewSources.some(source => 
        source.enabled !== defaultReviewSources.find(def => def.id === source.id)?.enabled
      );
      
      if (!hasSyncedData) {
        console.log('No synced data detected, using defaults');
        setReviewSources(defaultReviewSources);
      } else {
        console.log('Synced data detected, keeping current reviewSources state');
      }
      
      // Always set review source settings (these are separate from individual source toggles)
      setReviewSourceSettings(defaultReviewSourceSettings);
    } catch (error) {
      console.error('Error loading review sources:', error);
      // Only fallback to defaults if we don't have synced data
      const hasSyncedData = reviewSources.some(source => 
        source.enabled !== defaultReviewSources.find(def => def.id === source.id)?.enabled
      );
      if (!hasSyncedData) {
        setReviewSources(defaultReviewSources);
      }
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
      // CRITICAL FIX: Sync all reviewSources state to settings.Sources before saving
      const syncedSources = { ...settings.Sources };
      reviewSources.forEach(source => {
        let enableKey = '';
        if (source.source_name === 'MyAnimeList') {
          enableKey = 'enable_myanimelist';
        } else {
          enableKey = `enable_${source.source_name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '')}`;
        }
        syncedSources[enableKey] = source.enabled;
        console.log(`Syncing for save: ${source.source_name} -> ${enableKey} = ${source.enabled}`);
      });
      
      const settingsToSave = {
        ...settings,
        Sources: syncedSources
      };
      
      console.log('Saving review settings:', settingsToSave);
      console.log('Sources being saved:', syncedSources);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_review.yml`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settingsToSave),
      });

      console.log('Save response status:', response.status);
      
      if (!response.ok) {
        const errorData = await response.text();
        console.error('Save failed with response:', errorData);
        throw new Error(`Failed to save settings: ${response.status}`);
      }

      const result = await response.json();
      console.log('Save successful:', result);
      
      // Update local settings state to match what was saved
      setSettings(settingsToSave);
      
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
    
    // CRITICAL FIX: Also update the settings when a source is toggled
    let enableKey = '';
    if (updatedSource.source_name === 'MyAnimeList') {
      enableKey = 'enable_myanimelist';
    } else {
      enableKey = `enable_${updatedSource.source_name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '')}`;
    }
    
    console.log(`Updating ${updatedSource.source_name}: ${enableKey} = ${updatedSource.enabled}`);
    
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
    const newSettings = {
      ...reviewSourceSettings,
      [key]: value
    };
    
    setReviewSourceSettings(newSettings);
    
    // Auto-save review source settings immediately
    saveReviewSourceSettings(newSettings);
  };
  
  // Save review source settings to database
  const saveReviewSourceSettings = async (settingsToSave: ReviewSourceSettings = reviewSourceSettings) => {
    try {
      console.log('Saving review source settings:', settingsToSave);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/review_source_settings`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settingsToSave),
      });

      if (!response.ok) {
        const errorData = await response.text();
        console.error('Save review source settings failed:', errorData);
        throw new Error(`Failed to save review source settings: ${response.status}`);
      }

      const result = await response.json();
      console.log('Review source settings saved successfully:', result);
      
    } catch (error) {
      console.error('Error saving review source settings:', error);
      toast.error('Failed to save review source settings', {
        description: error instanceof Error ? error.message : 'Unknown error occurred',
        duration: 3000
      });
    }
  };
  
  // Load review source settings from database
  const loadReviewSourceSettings = async () => {
    try {
      console.log('Loading review source settings...');
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/review_source_settings`);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Loaded review source settings:', data);
        
        if (data.config && Object.keys(data.config).length > 0) {
          // Merge with defaults to ensure all fields exist
          const mergedSettings = {
            ...defaultReviewSourceSettings,
            ...data.config
          };
          setReviewSourceSettings(mergedSettings);
          console.log('Review source settings loaded successfully:', mergedSettings);
        } else {
          console.log('No existing review source settings found, using defaults');
          setReviewSourceSettings(defaultReviewSourceSettings);
        }
      } else {
        console.log('Review source settings endpoint not found, using defaults');
        setReviewSourceSettings(defaultReviewSourceSettings);
      }
    } catch (error) {
      console.error('Error loading review source settings:', error);
      setReviewSourceSettings(defaultReviewSourceSettings);
    }
  };

  // Reorder sources
  const reorderSources = (newOrder: ReviewSource[]) => {
    console.log('🔄 Reordering sources:', newOrder.map(s => ({name: s.source_name, priority: s.priority})));
    
    // Update local reviewSources state
    setReviewSources(newOrder);
    
    // CRITICAL FIX: Also update the source_priority array in settings
    const newSourcePriority = newOrder.map(source => {
      // Map source names back to the format used in source_priority array
      if (source.source_name === 'MyAnimeList') return 'myanimelist';
      if (source.source_name === 'IMDb') return 'imdb';
      if (source.source_name === 'Rotten Tomatoes Critics') return 'rotten_tomatoes';
      if (source.source_name === 'Rotten Tomatoes Audience') return 'rotten_tomatoes_audience';
      if (source.source_name === 'Metacritic') return 'metacritic';
      if (source.source_name === 'TMDb') return 'tmdb';
      if (source.source_name === 'AniDB') return 'anidb';
      if (source.source_name === 'Letterboxd') return 'letterboxd';
      if (source.source_name === 'Trakt') return 'trakt';
      if (source.source_name === 'MDBList') return 'mdblist';
      // Fallback for any unmapped sources
      return source.source_name.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
    });
    
    console.log('📌 Updating source_priority array:', newSourcePriority);
    
    // Update settings.Sources.source_priority
    setSettings(prev => ({
      ...prev,
      Sources: {
        ...prev.Sources,
        source_priority: newSourcePriority
      }
    }));
    
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

  // Debug effect to monitor state changes
  useEffect(() => {
    console.log('🔍 STATE CHANGE DETECTED:');
    console.log('   📊 settings.Sources.enable_myanimelist:', settings.Sources?.enable_myanimelist);
    console.log('   📋 reviewSources MyAnimeList:', reviewSources.find(s => s.source_name === 'MyAnimeList')?.enabled);
    console.log('   📋 reviewSources enabled count:', reviewSources.filter(s => s.enabled).length);
    console.log('   📋 reviewSources enabled names:', reviewSources.filter(s => s.enabled).map(s => s.source_name));
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
