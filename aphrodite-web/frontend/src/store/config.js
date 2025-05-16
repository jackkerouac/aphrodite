import { defineStore } from 'pinia';
import api from '@/api';

export const useConfigStore = defineStore('config', {
  state: () => ({
    apiSettings: null,
    loading: false,
    error: null
  }),
  
  getters: {
    jellyfin: (state) => state.apiSettings?.api_keys?.Jellyfin?.[0] || {},
    omdb: (state) => state.apiSettings?.api_keys?.OMDB?.[0] || {},
    tmdb: (state) => state.apiSettings?.api_keys?.TMDB?.[0] || {},
    anidb: (state) => state.apiSettings?.api_keys?.aniDB?.[0] || {}
  },
  
  actions: {
    async fetchApiSettings() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.config.getConfig('settings.yaml');
        this.apiSettings = response.data.config;
      } catch (error) {
        console.error('Error fetching API settings:', error);
        this.error = error.response?.data?.error || 'Failed to fetch API settings';
      } finally {
        this.loading = false;
      }
    },
    
    async saveApiSettings() {
      this.loading = true;
      this.error = null;
      
      try {
        await api.config.updateConfig('settings.yaml', this.apiSettings);
      } catch (error) {
        console.error('Error saving API settings:', error);
        this.error = error.response?.data?.error || 'Failed to save API settings';
        throw error;
      } finally {
        this.loading = false;
      }
    },
    
    updateJellyfin(jellyfin) {
      if (!this.apiSettings) {
        this.apiSettings = { api_keys: {} };
      }
      
      if (!this.apiSettings.api_keys) {
        this.apiSettings.api_keys = {};
      }
      
      if (!this.apiSettings.api_keys.Jellyfin) {
        this.apiSettings.api_keys.Jellyfin = [{}];
      }
      
      this.apiSettings.api_keys.Jellyfin[0] = jellyfin;
    },
    
    updateOmdb(omdb) {
      if (!this.apiSettings) {
        this.apiSettings = { api_keys: {} };
      }
      
      if (!this.apiSettings.api_keys) {
        this.apiSettings.api_keys = {};
      }
      
      if (!this.apiSettings.api_keys.OMDB) {
        this.apiSettings.api_keys.OMDB = [{}];
      }
      
      this.apiSettings.api_keys.OMDB[0] = omdb;
    },
    
    updateTmdb(tmdb) {
      if (!this.apiSettings) {
        this.apiSettings = { api_keys: {} };
      }
      
      if (!this.apiSettings.api_keys) {
        this.apiSettings.api_keys = {};
      }
      
      if (!this.apiSettings.api_keys.TMDB) {
        this.apiSettings.api_keys.TMDB = [{}];
      }
      
      this.apiSettings.api_keys.TMDB[0] = tmdb;
    },
    
    updateAnidb(anidb) {
      if (!this.apiSettings) {
        this.apiSettings = { api_keys: {} };
      }
      
      if (!this.apiSettings.api_keys) {
        this.apiSettings.api_keys = {};
      }
      
      if (!this.apiSettings.api_keys.aniDB) {
        this.apiSettings.api_keys.aniDB = [{}];
      }
      
      this.apiSettings.api_keys.aniDB[0] = anidb;
    }
  }
});
