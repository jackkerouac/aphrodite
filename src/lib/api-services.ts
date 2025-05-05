// Use string identifiers instead of JSX components
import { ApiService, ApiSettingField } from '@/hooks/useApiSettings';
import { 
  isValidUrl, 
  validateJellyfinConfig, 
  validateOmdbConfig,
  validateTmdbConfig,
  validateAnidbConfig
} from './validation';

// Import the API client
import apiClient from './api-client';

// Service icon identifiers (not actual JSX)
export const serviceIconNames = {
  jellyfin: 'server',
  omdb: 'film',
  tmdb: 'film',
  anidb: 'database'
};

// Service descriptions
export const serviceDescriptions = {
  jellyfin: 'Connect to your Jellyfin media server to access your media library.',
  omdb: 'Open Movie Database API for accessing movie and TV show metadata.',
  tmdb: 'The Movie Database API for accessing comprehensive movie and TV show metadata.',
  anidb: 'AniDB anime database for accessing anime metadata and artwork.',
};

// Field definitions for each service
export const serviceFields: Record<string, ApiSettingField[]> = {
  jellyfin: [
    {
      id: 'url',
      label: 'Jellyfin URL',
      placeholder: 'https://jellyfin.example.com',
      description: 'The base URL of your Jellyfin server (e.g., https://jellyfin.example.com)',
      required: true,
    },
    {
      id: 'apiKey',
      label: 'API Key',
      placeholder: 'Enter your API key',
      secure: true,
      description: 'Your Jellyfin API key for authentication',
      required: true,
    },
    {
      id: 'userId',
      label: 'User ID',
      placeholder: 'Enter your Jellyfin user ID',
      description: 'Your Jellyfin user ID for authentication',
      required: true,
    },
  ],
  omdb: [
    {
      id: 'apiKey',
      label: 'API Key',
      placeholder: 'Enter your OMDB API key',
      secure: true,
      description: 'Your OMDB API key for accessing movie and TV show data',
      required: true,
    },
  ],
  tmdb: [
    {
      id: 'apiKey',
      label: 'API Key',
      placeholder: 'Enter your TMDB API key',
      secure: true,
      description: 'Your TMDB API key for accessing movie and TV show data',
      required: true,
    },
  ],
  anidb: [
    {
      id: 'username',
      label: 'Username',
      placeholder: 'Enter your AniDB username',
      description: 'Your AniDB username for authentication',
      required: true,
    },
    {
      id: 'password',
      label: 'Password',
      placeholder: 'Enter your AniDB password',
      secure: true,
      description: 'Your AniDB password for authentication',
      required: true,
    },
    {
      id: 'client',
      label: 'Client',
      placeholder: 'aphrodite',
      description: 'The client name to identify your application to AniDB',
      required: true,
    },
    {
      id: 'version',
      label: 'Version',
      placeholder: '1',
      description: 'The version number of your client',
      required: true,
    },
    {
      id: 'language',
      label: 'Language',
      placeholder: 'en',
      description: 'Preferred language for AniDB responses (e.g., en, jp)',
      required: false,
    },
    {
      id: 'cacheExpiration',
      label: 'Cache Expiration',
      placeholder: '60',
      description: 'Cache expiration time in minutes',
      required: false,
    },
  ],
};

// Define API services with their fetch, save, and test methods
export const apiServices: Record<string, ApiService> = {
  jellyfin: {
    id: 'jellyfin',
    name: 'Jellyfin',

    // fetchSettings must return an object whose keys match your field IDs: url, apiKey, userId
    fetchSettings: async () => {
      try {
        // Fetch settings directly through the API client
        console.log('🔧 [apiServices] Jellyfin fetchSettings() called');
        
        // The client already handles the mapping
        const settings = await apiClient.jellyfin.getSettings();
        console.log('🔧 [apiServices] Jellyfin settings received:', settings);
        
        // Ensure we have proper field values
        if (!settings.url && !settings.apiKey && !settings.userId) {
          console.warn('⚠️ [apiServices] All Jellyfin fields are empty!');
        }
        
        return settings;
      } catch (error) {
        console.error('❌ [apiServices] Error fetching Jellyfin settings:', error);
        if (import.meta.env.DEV) {
          console.log('💡 [apiServices] Returning default values in DEV mode');
          return { url: '', apiKey: '', userId: '' };
        }
        throw error;
      }
    },


    saveSettings: async (values) => {
      // Log the values received by the saveSettings function
      console.log('🔴 [apiServices] Jellyfin saveSettings received values:', values);
      
      // Basic validation
      if (!values.url) {
        throw new Error('Jellyfin URL is required');
      }
      if (!values.apiKey) {
        throw new Error('API Key is required');
      }
      if (!values.userId) {
        throw new Error('User ID is required');
      }
      
      // Prepare the payload exactly as the backend expects it
      const payload = {
        jellyfin_url: values.url,
        jellyfin_api_key: values.apiKey,
        jellyfin_user_id: values.userId
      };
      
      console.log('🔴 [apiServices] Jellyfin saveSettings sending payload:', payload);
      return apiClient.jellyfin.saveSettings(payload);
    },
    testConnection: async (values) => {
      // Log the values received by the testConnection function
      console.log('🔴 [apiServices] Jellyfin testConnection received values:', values);
      
      // Basic validation
      if (!values.url) {
        throw new Error('Jellyfin URL is required');
      }
      if (!values.apiKey) {
        throw new Error('API Key is required');
      }
      if (!values.userId) {
        throw new Error('User ID is required');
      }
      
      // Prepare the payload exactly as the backend expects it
      const payload = {
        jellyfin_url: values.url,
        jellyfin_api_key: values.apiKey,
        jellyfin_user_id: values.userId
      };
      
      console.log('🔴 [apiServices] Jellyfin testConnection sending payload:', payload);
      return apiClient.jellyfin.testConnection(payload);
    },
  },
  
  // OMDB API service
  omdb: {
    id: 'omdb',
    name: 'OMDB',
    fetchSettings: async () => {
      try {
        return await apiClient.omdb.getSettings();
      } catch (error) {
        console.error('Error fetching OMDB settings:', error);
        
        if (import.meta.env.DEV) {
          return { apiKey: '' };
        }
        
        throw error;
      }
    },
    saveSettings: async (values) => {
      const validation = validateOmdbConfig(values);
      if (!validation.isValid) {
        throw new Error(Object.values(validation.errors)[0]);
      }
      
      return apiClient.omdb.saveSettings(values);
    },
    testConnection: async (values) => {
      const validation = validateOmdbConfig(values);
      if (!validation.isValid) {
        throw new Error(Object.values(validation.errors)[0]);
      }
      
      return apiClient.omdb.testConnection(values);
    },
  },
  
  // TMDB API service
  tmdb: {
    id: 'tmdb',
    name: 'TMDB',
    fetchSettings: async () => {
      try {
        return await apiClient.tmdb.getSettings();
      } catch (error) {
        console.error('Error fetching TMDB settings:', error);
        
        if (import.meta.env.DEV) {
          return { apiKey: '' };
        }
        
        throw error;
      }
    },
    saveSettings: async (values) => {
      const validation = validateTmdbConfig(values);
      if (!validation.isValid) {
        throw new Error(Object.values(validation.errors)[0]);
      }
      
      return apiClient.tmdb.saveSettings(values);
    },
    testConnection: async (values) => {
      const validation = validateTmdbConfig(values);
      if (!validation.isValid) {
        throw new Error(Object.values(validation.errors)[0]);
      }
      
      return apiClient.tmdb.testConnection(values);
    },
  },
  
  // AniDB API service
  anidb: {
    id: 'anidb',
    name: 'AniDB',
    fetchSettings: async () => {
      try {
        console.log('🔍 [apiServices] AniDB fetchSettings() called');
        const settings = await apiClient.anidb.getSettings();
        console.log('🔍 [apiServices] AniDB settings received:', { ...settings, password: '******' });
        return settings;
      } catch (error) {
        console.error('❌ [apiServices] Error fetching AniDB settings:', error);
        
        if (import.meta.env.DEV) {
          console.log('💡 [apiServices] Returning default AniDB values in DEV mode');
          return { 
            username: '', 
            password: '', 
            client: 'aphrodite',
            version: '1',
            language: 'en',
            cacheExpiration: '60'
          };
        }
        
        throw error;
      }
    },
    saveSettings: async (values) => {
      console.log('💾 [apiServices] AniDB saveSettings received values:', { ...values, password: '******' });
      
      const validation = validateAnidbConfig(values);
      if (!validation.isValid) {
        console.error('❌ [apiServices] AniDB validation failed:', validation.errors);
        throw new Error(Object.values(validation.errors)[0]);
      }
      
      console.log('🔄 [apiServices] AniDB validation passed, saving settings');
      return apiClient.anidb.saveSettings(values);
    },
    testConnection: async (values) => {
      console.log('🔍 [apiServices] AniDB testConnection received values:', { ...values, password: '******' });
      
      const validation = validateAnidbConfig(values);
      if (!validation.isValid) {
        console.error('❌ [apiServices] AniDB validation failed:', validation.errors);
        throw new Error(Object.values(validation.errors)[0]);
      }
      
      console.log('🔄 [apiServices] AniDB validation passed, testing connection');
      return apiClient.anidb.testConnection(values);
    },
  },
};
