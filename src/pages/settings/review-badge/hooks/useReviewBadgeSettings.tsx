import { useState, useEffect } from 'react';
import apiClient, { ApiError } from '@/lib/api-client';
import { reviewSources } from '../constants';

// Configuration
const USE_SIMULATION = true; // Set to false when backend API is implemented
const SIMULATION_DELAY = 800; // Milliseconds to simulate network delay

// For simulation mode - store settings in memory
let savedSimulationSettings: ReviewBadgeSettings | null = null;

export interface ReviewBadgeSettings {
  position: string;
  badge_layout: string;
  display_sources: string[];
  source_order: string[];
  show_logo: boolean;
  logo_size: number;
  logo_position: string;
  logoTextSpacing: number;
  score_format: string;
  size: number;
  margin: number;
  spacing: number;
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
  font_family: string;
  font_size: number;
  font_weight: number;
  text_color: string;
  text_transparency: number;
}

export interface UseReviewBadgeSettingsReturn {
  settings: ReviewBadgeSettings;
  loading: boolean;
  error: Error | null;
  saving: boolean;
  isSaveDisabled: boolean;
  showSuccessNotification: boolean;
  handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  handleNumberChange: (key: string, value: number) => void;
  handleColorChange: (key: string, value: string) => void;
  handleToggleChange: (key: string, value: boolean) => void;
  handleSelectChange: (key: string, value: string) => void;
  handleArrayChange: (key: string, value: string[]) => void;
  handlePositionChange: (value: string) => void;
  handleSave: () => Promise<void>;
  setError: React.Dispatch<React.SetStateAction<Error | null>>;
  setShowSuccessNotification: React.Dispatch<React.SetStateAction<boolean>>;
}

const defaultSettings: ReviewBadgeSettings = {
  position: 'top-right',
  badge_layout: 'horizontal',
  display_sources: ['IMDB', 'TMDB'],
  source_order: ['IMDB', 'TMDB', 'RottenTomatoes', 'Metacritic', 'AniDB'],
  show_logo: true,
  logo_size: 24,
  logo_position: 'top',
  logoTextSpacing: 5,
  score_format: 'decimal',
  size: 100,
  margin: 10,
  spacing: 5,
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
  z_index: 1,
  font_family: 'Inter',
  font_size: 16,
  font_weight: 600,
  text_color: '#ffffff',
  text_transparency: 0,
};

// Helper function to validate settings
const validateSettings = (settings: ReviewBadgeSettings): { isValid: boolean; missingFields: string[] } => {
  const requiredFields = [
    'position',
    'badge_layout',
    'size',
    'margin',
    'background_color',
    'background_transparency',
    'border_radius',
    'border_width',
    'border_color',
    'border_transparency',
    'z_index',
    'font_family',
    'font_size',
    'font_weight',
    'text_color',
    'text_transparency'
  ];
  
  const missingFields: string[] = [];
  
  for (const field of requiredFields) {
    // Check if field is undefined or empty string for string fields
    if (settings[field as keyof ReviewBadgeSettings] === undefined || 
        (typeof settings[field as keyof ReviewBadgeSettings] === 'string' && 
         settings[field as keyof ReviewBadgeSettings] === '')) {
      missingFields.push(field);
    }
  }
  
  return {
    isValid: missingFields.length === 0,
    missingFields
  };
};

export const useReviewBadgeSettings = (): UseReviewBadgeSettingsReturn => {
  const [settings, setSettings] = useState<ReviewBadgeSettings>(defaultSettings);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [saving, setSaving] = useState(false);
  const [isSaveDisabled, setIsSaveDisabled] = useState(false);
  const [showSuccessNotification, setShowSuccessNotification] = useState(false);

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
          } else {
            console.log('No saved settings found in simulation mode, using defaults');
          }
          
          setLoading(false);
          return;
        }
        
        // Use the API client to fetch settings
        console.log('🔄 [useReviewBadgeSettings] Fetching review badge settings...');
        
        try {
          // This will need to be implemented in your API client
          // const data = await apiClient.reviewBadge.getSettings();
          // console.log('✅ [useReviewBadgeSettings] Settings loaded:', data);
          
          // For now, use default settings until API is implemented
          const data = defaultSettings;
          
          // Make sure we have all required fields, filling in with defaults if needed
          const mergedSettings = {
            ...defaultSettings, // Start with defaults
            ...data, // Override with loaded data
          };
          
          console.log('📊 [useReviewBadgeSettings] Merged settings:', mergedSettings);
          
          // Validate the merged settings
          const validation = validateSettings(mergedSettings);
          if (!validation.isValid) {
            console.warn('⚠️ [useReviewBadgeSettings] Merged settings missing fields:', validation.missingFields);
            console.warn('⚠️ [useReviewBadgeSettings] Using defaults for missing fields');
          }
          
          // Update settings
          setSettings(mergedSettings);
        } catch (apiError) {
          console.error('❌ [useReviewBadgeSettings] API Error:', apiError);
          
          // If 404 Not Found, use defaults (the API client may already handle this)
          if (apiError instanceof ApiError && apiError.status === 404) {
            console.log('ℹ️ [useReviewBadgeSettings] No settings found, using defaults');
            return;
          }
          
          throw apiError;
        }
      } catch (err: any) {
        console.error('❌ [useReviewBadgeSettings] Error loading settings:', err);
        setError(err);
      } finally {
        setLoading(false);
      }
    };
    
    fetchSettings();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value, type } = e.target;
    
    setSettings(prevSettings => ({
      ...prevSettings,
      [name]: type === 'number' ? parseFloat(value) : value,
    }));
  };
  
  const handleNumberChange = (key: string, value: number) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [key]: value,
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

  const handleSelectChange = (key: string, value: string) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [key]: value,
    }));
  };

  const handleArrayChange = (key: string, value: string[]) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      [key]: value,
    }));
  };

  const handlePositionChange = (value: string) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      position: value,
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
      
      // Make sure all required fields are populated
      const settingsToSave = {
        ...defaultSettings, // Start with defaults
        ...settings, // Override with current settings
      };
      
      // Validate settings before saving
      const validation = validateSettings(settingsToSave);
      if (!validation.isValid) {
        console.error('❌ [useReviewBadgeSettings] Missing required fields:', validation.missingFields);
        throw new Error(`Missing required fields: ${validation.missingFields.join(', ')}`);
      }
      
      console.log('📤 [useReviewBadgeSettings] Saving review badge settings:', settingsToSave);
      
      try {
        // This will need to be implemented in your API client
        // await apiClient.reviewBadge.saveSettings(settingsToSave);
        console.log('✅ [useReviewBadgeSettings] Settings saved successfully');
        
        // Update the settings state to reflect the saved values
        setSettings(settingsToSave);
        
        // Set success state
        setShowSuccessNotification(true);
        
        // Hide success notification after a delay
        setTimeout(() => {
          setShowSuccessNotification(false);
        }, 3000);
      } catch (apiError) {
        console.error('❌ [useReviewBadgeSettings] API Error saving settings:', apiError);
        throw apiError;
      }
    } catch (err: any) {
      console.error('❌ [useReviewBadgeSettings] Error saving settings:', err);
      setError(err);
    } finally {
      setSaving(false);
      setIsSaveDisabled(false);
    }
  };

  return {
    settings,
    loading,
    error,
    saving,
    isSaveDisabled,
    showSuccessNotification,
    handleChange,
    handleNumberChange,
    handleColorChange,
    handleToggleChange,
    handleSelectChange,
    handleArrayChange,
    handlePositionChange,
    handleSave,
    setError,
    setShowSuccessNotification
  };
};
