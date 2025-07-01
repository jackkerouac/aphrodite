import { useState, useCallback } from 'react';
import { toast } from 'sonner';
import { saveSettingsWithCacheClear } from '@/lib/settings-utils';
import { loadAvailableFonts } from '@/lib/font-utils';
import { AudioSettings, AudioCoverageReport, AudioCacheStats, AudioDetectionTestResult } from './types';

const defaultSettings: AudioSettings = {
  General: {
    general_badge_size: 100,
    general_edge_padding: 30,
    general_badge_position: 'top-right',
    general_text_padding: 12,
    use_dynamic_sizing: true
  },
  Text: {
    font: 'AvenirNextLTProBold.otf',
    fallback_font: 'DejaVuSans.ttf',
    'text-color': '#FFFFFF',
    'text-size': 90
  },
  Background: {
    'background-color': '#000000',
    background_opacity: 40
  },
  Border: {
    'border-color': '#000000',
    'border-radius': 10,
    border_width: 1
  },
  Shadow: {
    shadow_enable: false,
    shadow_blur: 8,
    shadow_offset_x: 2,
    shadow_offset_y: 2
  },
  ImageBadges: {
    enable_image_badges: true,
    codec_image_directory: 'images/codec',
    fallback_to_text: true,
    image_padding: 0,
    image_mapping: {
      'ATMOS': 'Atmos.png',
      'DOLBY DIGITAL PLUS': 'DigitalPlus.png',
      'DTS-HD MA': 'DTS-HD.png',
      'DTS-X': 'DTS-X.png',
      'TRUEHD': 'TrueHD.png',
      'TRUEHD ATMOS': 'TrueHD-Atmos.png'
    }
  },
  EnhancedDetection: {
    enabled: true,
    fallback_rules: {
      'dts-hd': 'dts',
      'truehd-atmos': 'truehd'
    },
    atmos_detection_patterns: [
      'atmos',
      'dolby atmos',
      'truehd atmos',
      'dd+ atmos'
    ],
    dts_x_detection_patterns: [
      'dts-x',
      'dtsx',
      'dts:x'
    ],
    priority_order: [
      'atmos',
      'dts-x',
      'truehd',
      'dts-hd',
      'dd+',
      'dts'
    ]
  },
  Performance: {
    enable_parallel_processing: true,
    enable_caching: true,
    cache_ttl_hours: 24,
    max_episodes_to_sample: 5
  }
};

export function useAudioSettings() {
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [settings, setSettings] = useState<AudioSettings>(defaultSettings);
  const [availableFonts, setAvailableFonts] = useState<string[]>([]);

  // Load fonts
  const loadFonts = useCallback(async () => {
    try {
      const fonts = await loadAvailableFonts();
      setAvailableFonts(fonts);
    } catch (error) {
      console.error('Error loading fonts:', error);
      setAvailableFonts([]);
    }
  }, []);

  // Load settings from API
  const loadSettings = useCallback(async () => {
    setLoading(true);
    
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/config/badge_settings_audio.yml`);
      const data = await response.json();
      
      if (data.config && Object.keys(data.config).length > 0) {
        // Merge loaded config with defaults to ensure all fields exist
        const mergedSettings = {
          ...defaultSettings,
          ...data.config,
          General: { ...defaultSettings.General, ...data.config.General },
          Text: { ...defaultSettings.Text, ...data.config.Text },
          Background: { ...defaultSettings.Background, ...data.config.Background },
          Border: { ...defaultSettings.Border, ...data.config.Border },
          Shadow: { ...defaultSettings.Shadow, ...data.config.Shadow },
          ImageBadges: { ...defaultSettings.ImageBadges, ...data.config.ImageBadges },
          EnhancedDetection: { ...defaultSettings.EnhancedDetection, ...data.config.EnhancedDetection },
          Performance: { ...defaultSettings.Performance, ...data.config.Performance }
        };
        setSettings(mergedSettings);
      } else {
        setSettings(defaultSettings);
      }
    } catch (error) {
      console.error('Error loading audio settings:', error);
      toast.error('Failed to load audio badge settings');
      setSettings(defaultSettings);
    } finally {
      setLoading(false);
    }
  }, []);

  // Save settings to API
  const saveSettings = useCallback(async () => {
    setSaving(true);
    
    try {
      await saveSettingsWithCacheClear('badge_settings_audio.yml', settings);
      toast.success('Audio badge settings saved successfully!');
    } catch (error) {
      console.error('Error saving audio settings:', error);
      toast.error('Failed to save audio badge settings');
    } finally {
      setSaving(false);
    }
  }, [settings]);

  // Update a setting
  const updateSetting = useCallback((path: string, value: any) => {
    setSettings(prev => {
      const keys = path.split('.');
      const newSettings = { ...prev };
      let current: any = newSettings;
      
      for (let i = 0; i < keys.length - 1; i++) {
        current[keys[i]] = { ...current[keys[i]] };
        current = current[keys[i]];
      }
      
      current[keys[keys.length - 1]] = value;
      return newSettings;
    });
  }, []);

  // Add new audio mapping
  const addAudioMapping = useCallback((codec: string, image: string) => {
    if (codec && image) {
      setSettings(prev => ({
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: {
            ...prev.ImageBadges.image_mapping,
            [codec]: image
          }
        }
      }));
      return true;
    }
    return false;
  }, []);

  // Remove audio mapping
  const removeAudioMapping = useCallback((codec: string) => {
    setSettings(prev => {
      const newImageMapping = { ...prev.ImageBadges.image_mapping };
      delete newImageMapping[codec];
      return {
        ...prev,
        ImageBadges: {
          ...prev.ImageBadges,
          image_mapping: newImageMapping
        }
      };
    });
  }, []);

  // Update codec name in mapping
  const updateCodecName = useCallback((oldName: string, newName: string) => {
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
  }, []);

  // Diagnostic functions
  const runAudioCoverageAnalysis = useCallback(async (): Promise<AudioCoverageReport | null> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings/audio/coverage`);
      if (!response.ok) throw new Error(`Analysis failed: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error('Audio coverage analysis failed:', error);
      toast.error('Failed to analyze audio coverage');
      return null;
    }
  }, []);

  const getCacheStats = useCallback(async (): Promise<AudioCacheStats | null> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings/audio/cache/stats`);
      if (!response.ok) throw new Error(`Cache stats failed: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error('Audio cache stats failed:', error);
      toast.error('Failed to get cache statistics');
      return null;
    }
  }, []);

  const clearAudioCache = useCallback(async (): Promise<boolean> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings/audio/cache`, {
        method: 'DELETE'
      });
      if (!response.ok) throw new Error(`Cache clear failed: ${response.statusText}`);
      toast.success('Audio cache cleared successfully');
      return true;
    } catch (error) {
      console.error('Audio cache clear failed:', error);
      toast.error('Failed to clear audio cache');
      return false;
    }
  }, []);

  const testEnhancedDetection = useCallback(async (testData?: any): Promise<AudioDetectionTestResult | null> => {
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/v1/settings/audio/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(testData || {})
      });
      if (!response.ok) throw new Error(`Detection test failed: ${response.statusText}`);
      return await response.json();
    } catch (error) {
      console.error('Audio detection test failed:', error);
      toast.error('Failed to test enhanced detection');
      return null;
    }
  }, []);

  return {
    loading,
    saving,
    settings,
    availableFonts,
    loadSettings,
    loadFonts,
    saveSettings,
    updateSetting,
    addAudioMapping,
    removeAudioMapping,
    updateCodecName,
    // Diagnostic functions
    runAudioCoverageAnalysis,
    getCacheStats,
    clearAudioCache,
    testEnhancedDetection
  };
}
