import { useState, useEffect } from 'react';
import apiClient, { ApiError } from '@/lib/api-client';

// Configuration
const USE_SIMULATION = false; // Set to false when backend API is implemented
const SIMULATION_DELAY = 800; // Milliseconds to simulate network delay

// For simulation mode - store settings in memory
let savedSimulationSettings: ResolutionBadgeSettings | null = null;

export interface ResolutionBadgeSettings {
  resolution_type: string;
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
}

export interface UseResolutionBadgeSettingsReturn {
  settings: ResolutionBadgeSettings;
  loading: boolean;
  error: Error | null;
  saving: boolean;
  isSaveDisabled: boolean;
  showSuccessNotification: boolean;
  selectedResolution: string;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleColorChange: (key: string, value: string) => void;
  handleToggleChange: (key: string, value: boolean) => void;
  handleSave: () => Promise<void>;
  handlePositionChange: (value: string) => void;
  handleResolutionChange: (value: string) => void;
  setError: React.Dispatch<React.SetStateAction<Error | null>>;
  setShowSuccessNotification: React.Dispatch<React.SetStateAction<boolean>>;
}

const defaultSettings: ResolutionBadgeSettings = {
  resolution_type: '1080',
  margin: 10,
  position: 'top-left',
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
const validateSettings = (settings: ResolutionBadgeSettings): { isValid: boolean; missingFields: string[] } => {
  const requiredFields = [
    'size',
    'margin',
    'position',
    'resolution_type',
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
    if (settings[field as keyof ResolutionBadgeSettings] === undefined || 
        (typeof settings[field as keyof ResolutionBadgeSettings] === 'string' && 
         settings[field as keyof ResolutionBadgeSettings] === '')) {
      missingFields.push(field);
    }
  }
  
  return {
    isValid: missingFields.length === 0,
    missingFields
  };
};

export const useResolutionBadgeSettings = (): UseResolutionBadgeSettingsReturn => {
  const [settings, setSettings] = useState<ResolutionBadgeSettings>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [saving, setSaving] = useState(false);
  const [isSaveDisabled, setIsSaveDisabled] = useState(false);
  const [showSuccessNotification, setShowSuccessNotification] = useState(false);
  const [selectedResolution, setSelectedResolution] = useState(settings.resolution_type || '1080');

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
            
            if (savedSimulationSettings.resolution_type) {
              setSelectedResolution(savedSimulationSettings.resolution_type);
            }
          } else {
            console.log('No saved settings found in simulation mode, using defaults');
          }
          
          setLoading(false);
          return;
        }
        
        // Use the API client to fetch settings
        console.log('🔄 [useResolutionBadgeSettings] Fetching resolution badge settings...');
        
        try {
          // Using the resolutionBadge endpoint from the apiClient
          const data = await apiClient.resolutionBadge.getSettings();
          console.log('✅ [useResolutionBadgeSettings] Settings loaded:', data);
          
          // Make sure we have all required fields, filling in with defaults if needed
          const mergedSettings = {
            ...defaultSettings, // Start with defaults
            ...data, // Override with loaded data
          };
          
          console.log('📊 [useResolutionBadgeSettings] Merged settings:', mergedSettings);
          
          // Validate the merged settings
          const validation = validateSettings(mergedSettings);
          if (!validation.isValid) {
            console.warn('⚠️ [useResolutionBadgeSettings] Merged settings missing fields:', validation.missingFields);
            console.warn('⚠️ [useResolutionBadgeSettings] Using defaults for missing fields');
          }
          
          // Update settings
          setSettings(mergedSettings);
          
          // Update selected resolution if it exists in the loaded data
          if (mergedSettings.resolution_type) {
            setSelectedResolution(mergedSettings.resolution_type);
          }
        } catch (apiError) {
          console.error('❌ [useResolutionBadgeSettings] API Error:', apiError);
          
          // If 404 Not Found, use defaults (the API client may already handle this)
          if (apiError instanceof ApiError && apiError.status === 404) {
            console.log('ℹ️ [useResolutionBadgeSettings] No settings found, using defaults');
            return;
          }
          
          throw apiError;
        }
      } catch (err: any) {
        console.error('❌ [useResolutionBadgeSettings] Error loading settings:', err);
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
      
      // Make sure resolution_type is set correctly by using the selectedResolution value
      const updatedSettings = {
        ...settings,
        resolution_type: selectedResolution
      };
      
      // Make sure all required fields are populated
      const settingsToSave = {
        ...defaultSettings, // Start with defaults
        ...updatedSettings, // Override with current settings
      };
      
      console.log('🔍 [useResolutionBadgeSettings] Values before validation:');
      console.log('  - settings.resolution_type:', settings.resolution_type);
      console.log('  - selectedResolution:', selectedResolution);
      console.log('  - updatedSettings.resolution_type:', updatedSettings.resolution_type);
      console.log('  - settingsToSave.resolution_type:', settingsToSave.resolution_type);
      
      // Validate settings before saving
      const validation = validateSettings(settingsToSave);
      if (!validation.isValid) {
        console.error('❌ [useResolutionBadgeSettings] Missing required fields:', validation.missingFields);
        throw new Error(`Missing required fields: ${validation.missingFields.join(', ')}`);
      }
      
      console.log('📤 [useResolutionBadgeSettings] Saving resolution badge settings:', settingsToSave);
      
      try {
        // Using the resolutionBadge endpoint from the apiClient
        await apiClient.resolutionBadge.saveSettings(settingsToSave);
        console.log('✅ [useResolutionBadgeSettings] Settings saved successfully');
        
        // Update the settings state to reflect the saved values
        setSettings(settingsToSave);
        
        // Set success state
        setShowSuccessNotification(true);
        
        // Hide success notification after a delay
        setTimeout(() => {
          setShowSuccessNotification(false);
        }, 3000);
      } catch (apiError) {
        console.error('❌ [useResolutionBadgeSettings] API Error saving settings:', apiError);
        throw apiError;
      }
    } catch (err: any) {
      console.error('❌ [useResolutionBadgeSettings] Error saving settings:', err);
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
  
  const handleResolutionChange = (value: string) => {
    console.log('🔄 [useResolutionBadgeSettings] Resolution changed to:', value);
    setSettings(prevSettings => ({
      ...prevSettings,
      resolution_type: value,
    }));
    setSelectedResolution(value);
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
    handleResolutionChange,
    setError,
    showSuccessNotification,
    setShowSuccessNotification,
    selectedResolution
  };
};
