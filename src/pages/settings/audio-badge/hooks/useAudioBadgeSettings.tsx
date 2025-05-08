import { useState, useEffect, useRef } from 'react';
import apiClient, { ApiError } from '@/lib/api-client';
import { captureBadgeAsBase64 } from '@/lib/utils/capture-badge';

// Configuration
const USE_SIMULATION = false;
const SIMULATION_DELAY = 800;

// For simulation mode - store settings in memory
let savedSimulationSettings: AudioBadgeSettings | null = null;

export interface AudioBadgeSettings {
  audio_codec_type: string;
  margin: number;
  position: string;
  size: number; // Size as percentage (100% = original size)
  background_color: string;
  background_transparency: number;
  border_radius: number;
  border_width: number;
  border_color: string;
  border_transparency: number;
  shadow_toggle: boolean;
  shadow_color: string;
  shadow_blur_radius: number;
  shadow_offset_x: number;
  shadow_offset_y: number;
  z_index: number;
  badge_image?: string; // Base64 encoded image data
}

export interface UseAudioBadgeSettingsReturn {
  settings: AudioBadgeSettings;
  loading: boolean;
  error: Error | null;
  saving: boolean;
  isSaveDisabled: boolean;
  showSuccessNotification: boolean;
  selectedAudioCodec: string;
  badgeRef: React.RefObject<HTMLDivElement>;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleColorChange: (key: string, value: string) => void;
  handleToggleChange: (key: string, value: boolean) => void;
  handleSave: () => Promise<void>;
  handlePositionChange: (value: string) => void;
  handleAudioCodecChange: (value: string) => void;
  setError: React.Dispatch<React.SetStateAction<Error | null>>;
  setShowSuccessNotification: React.Dispatch<React.SetStateAction<boolean>>;
}

const defaultSettings: AudioBadgeSettings = {
  audio_codec_type: 'dolby_atmos',
  margin: 10,
  position: 'top-right',
  size: 100, // Size as percentage (100% = original size)
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
  z_index: 1
};

// Helper function to validate settings
const validateSettings = (settings: AudioBadgeSettings): { isValid: boolean; missingFields: string[] } => {
  const requiredFields = [
    'size',
    'margin',
    'position',
    'audio_codec_type',
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
    // Check if field is undefined or empty string for string fields
    if (settings[field as keyof AudioBadgeSettings] === undefined || 
        (typeof settings[field as keyof AudioBadgeSettings] === 'string' && 
         settings[field as keyof AudioBadgeSettings] === '')) {
      missingFields.push(field);
    }
  }
  
  return {
    isValid: missingFields.length === 0,
    missingFields
  };
};

export const useAudioBadgeSettings = (): UseAudioBadgeSettingsReturn => {
  const [settings, setSettings] = useState<AudioBadgeSettings>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [saving, setSaving] = useState(false);
  const [isSaveDisabled, setIsSaveDisabled] = useState(false);
  const [showSuccessNotification, setShowSuccessNotification] = useState(false);
  const [selectedAudioCodec, setSelectedAudioCodec] = useState(settings.audio_codec_type || 'dolby_atmos');
  const badgeRef = useRef<HTMLDivElement>(null);

  // Load settings from the API when component mounts
  useEffect(() => {
    const fetchSettings = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // Check if using simulation mode
        if (USE_SIMULATION) {
          // Simulate network delay
          await new Promise(resolve => setTimeout(resolve, SIMULATION_DELAY));
          
          // If we have saved settings, use them
          if (savedSimulationSettings) {
            console.log('Using simulated saved settings:', savedSimulationSettings);
            
            setSettings(prevSettings => ({
              ...prevSettings,
              ...savedSimulationSettings,
            }));
            
            if (savedSimulationSettings.audio_codec_type) {
              setSelectedAudioCodec(savedSimulationSettings.audio_codec_type);
            }
          } else {
            console.log('No saved settings found in simulation mode, using defaults');
          }
          
          setLoading(false);
          return;
        }
        
        // Use the API client to fetch settings
        console.log('🔄 [useAudioBadgeSettings] Fetching audio badge settings...');
        
        
        try {
          // Using the audioBadge endpoint from the apiClient
          const data = await apiClient.audioBadge.getSettings();
          console.log('✅ [useAudioBadgeSettings] Settings loaded:', data);
          
          // Make sure we have all required fields, filling in with defaults if needed
          const mergedSettings = {
            ...defaultSettings, // Start with defaults
            ...data, // Override with loaded data
          };
          
          console.log('📊 [useAudioBadgeSettings] Merged settings:', mergedSettings);
          
          // Validate the merged settings
          const validation = validateSettings(mergedSettings);
          if (!validation.isValid) {
            console.warn('⚠️ [useAudioBadgeSettings] Merged settings missing fields:', validation.missingFields);
            console.warn('⚠️ [useAudioBadgeSettings] Using defaults for missing fields');
          }
          
          // Update settings
          setSettings(mergedSettings);
          
          // Update selected audio codec if it exists in the loaded data
          if (mergedSettings.audio_codec_type) {
            setSelectedAudioCodec(mergedSettings.audio_codec_type);
          }
        } catch (apiError) {
          console.error('❌ [useAudioBadgeSettings] API Error:', apiError);
          
          // If 404 Not Found, use defaults (the API client may already handle this)
          if (apiError instanceof ApiError && apiError.status === 404) {
            console.log('ℹ️ [useAudioBadgeSettings] No settings found, using defaults');
            return;
          }
          
          throw apiError;
        }
      } catch (err: any) {
        console.error('❌ [useAudioBadgeSettings] Error loading settings:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSettings();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setSettings(prevSettings => ({
      ...prevSettings,
      [name]: name.includes('transparency') || name.includes('size') ? parseFloat(value) : value,
    }));
  };
  
  const handleColorChange = (key: string, value: string) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [key]: value,
    }));
  };
  
  const handleToggleChange = (key: string, value: boolean) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [key]: value,
    }));
  };

  const handleSave = async () => {
    console.log('🔥 handleSave function called');
    try {
      setSaving(true);
      setIsSaveDisabled(true);
      setError(null);

      // Check if using simulation mode
      if (USE_SIMULATION) {
        // Simulate network delay
        await new Promise(resolve => setTimeout(resolve, SIMULATION_DELAY));
        // Store settings in the simulation variable
        savedSimulationSettings = { ...settings };
        console.log('Saved settings in simulation mode:', savedSimulationSettings);

        // Set success state
        setShowSuccessNotification(true);
        // Hide success notification after a delay
        setTimeout(() => {
          setShowSuccessNotification(false);
        }, 3000);
        setSaving(false);
        setIsSaveDisabled(false);
        return;
      }

      // Capture the badge image if badgeRef is available
      let badgeImage = null;
      if (badgeRef.current) {
        console.log('📸 [useAudioBadgeSettings] Capturing badge image...');
        try {
          badgeImage = await captureBadgeAsBase64(badgeRef);
          console.log('✅ [useAudioBadgeSettings] Badge image captured successfully');
          console.log('📏 [useAudioBadgeSettings] Badge image length:', badgeImage ? badgeImage.length : 0);
          // Log the first 100 characters of the image data to verify format
          console.log('🔍 [useAudioBadgeSettings] Badge image preview:', badgeImage ? badgeImage.substring(0, 100) + '...' : 'null');
        } catch (captureError) {
          console.error('❌ [useAudioBadgeSettings] Error capturing badge image:', captureError);
          // Continue even if image capture fails - we'll just save settings without the image
        }
      } else {
        console.warn('⚠️ [useAudioBadgeSettings] Badge reference not available, cannot capture image');
      }

      // Make sure audio_codec_type is set correctly by using the selectedAudioCodec value
      const updatedSettings = {
        ...settings,
        audio_codec_type: selectedAudioCodec,
        badge_image: badgeImage // Include the captured image in the settings
      };

      // Make sure all required fields are populated
      const settingsToSave = {
        ...defaultSettings, // Start with defaults
        ...updatedSettings, // Override with current settings
      };

      console.log('🔍 [useAudioBadgeSettings] Values before validation:');
      console.log('  - settings.audio_codec_type:', settings.audio_codec_type);
      console.log('  - selectedAudioCodec:', selectedAudioCodec);
      console.log('  - updatedSettings.audio_codec_type:', updatedSettings.audio_codec_type);
      console.log('  - settingsToSave.audio_codec_type:', settingsToSave.audio_codec_type);
      console.log('  - Has badge image:', !!badgeImage);

      // Validate settings before saving
      const validation = validateSettings(settingsToSave);
      if (!validation.isValid) {
        console.error('❌ [useAudioBadgeSettings] Missing required fields:', validation.missingFields);
        throw new Error(`Missing required fields: ${validation.missingFields.join(', ')}`);
      }

      console.log('📤 [useAudioBadgeSettings] Saving audio badge settings:', settingsToSave);
      console.log('🔍 [useAudioBadgeSettings] settingsToSave object:', JSON.stringify(settingsToSave, null, 2));
      try {
        // Using the audioBadge endpoint from the apiClient
        await apiClient.audioBadge.saveSettings(settingsToSave);
        console.log('✅ [useAudioBadgeSettings] Settings saved successfully');

        // Update the settings state to reflect the saved values
        setSettings(settingsToSave);
        // Set success state
        setShowSuccessNotification(true);
        // Hide success notification after a delay
        setTimeout(() => {
          setShowSuccessNotification(false);
        }, 3000);
      } catch (apiError) {
        console.error('❌ [useAudioBadgeSettings] API Error saving settings:', apiError);
        throw apiError;
      }
    } catch (err: any) {
      console.error('❌ [useAudioBadgeSettings] Error saving settings:', err);
      setError(err);
    } finally {
      setSaving(false);
      setIsSaveDisabled(false);
    }
  };

  const handlePositionChange = (value: string) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      position: value,
    }));
  };
  
  const handleAudioCodecChange = (value: string) => {
    console.log('🔄 [useAudioBadgeSettings] Audio codec changed to:', value);
    setSettings(prevSettings => ({
      ...prevSettings,
      audio_codec_type: value,
    }));
    setSelectedAudioCodec(value);
  };

  return {
    settings,
    loading,
    error,
    saving,
    handleChange,
    handleColorChange,
    handleToggleChange,
    handleSave,
    isSaveDisabled,
    handlePositionChange,
    handleAudioCodecChange,
    setError,
    showSuccessNotification,
    setShowSuccessNotification,
    selectedAudioCodec,
    badgeRef
  };
};