<template>
  <div class="api-settings">
    <h2 class="text-xl font-bold mb-4">API Settings</h2>
    
    <form @submit.prevent="saveSettings" class="space-y-6">
      <!-- Jellyfin Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">Jellyfin Connection</h3>
        
        <div class="grid grid-cols-1 gap-4">
          <div class="form-group">
            <label for="jellyfin-url" class="block text-sm font-medium text-gray-700 mb-1">Server URL</label>
            <input 
              id="jellyfin-url" 
              v-model="jellyfin.url" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="https://jellyfin.example.com"
            />
          </div>
          
          <div class="form-group">
            <label for="jellyfin-api-key" class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
            <input 
              id="jellyfin-api-key" 
              v-model="jellyfin.api_key" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Your Jellyfin API key"
            />
          </div>
          
          <div class="form-group">
            <label for="jellyfin-user-id" class="block text-sm font-medium text-gray-700 mb-1">User ID</label>
            <input 
              id="jellyfin-user-id" 
              v-model="jellyfin.user_id" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Your Jellyfin user ID"
            />
          </div>
          
          <div class="form-group">
            <button 
              type="button" 
              @click="testJellyfinConnection" 
              class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              :disabled="connectionTesting"
            >
              {{ connectionTesting ? 'Testing...' : 'Test Connection' }}
            </button>
            <span v-if="connectionStatus" :class="connectionStatus.success ? 'text-green-600' : 'text-red-600'" class="ml-2">
              {{ connectionStatus.message }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- OMDB Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">OMDB API</h3>
        
        <div class="grid grid-cols-1 gap-4">
          <div class="form-group">
            <label for="omdb-api-key" class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
            <input 
              id="omdb-api-key" 
              v-model="omdb.api_key" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Your OMDB API key"
            />
          </div>
          
          <div class="form-group">
            <label for="omdb-cache" class="block text-sm font-medium text-gray-700 mb-1">Cache Expiration (minutes)</label>
            <input 
              id="omdb-cache" 
              v-model.number="omdb.cache_expiration" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="60"
            />
          </div>
        </div>
      </div>
      
      <!-- TMDB Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">TMDB API</h3>
        
        <div class="grid grid-cols-1 gap-4">
          <div class="form-group">
            <label for="tmdb-api-key" class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
            <input 
              id="tmdb-api-key" 
              v-model="tmdb.api_key" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Your TMDB API key"
            />
          </div>
          
          <div class="form-group">
            <label for="tmdb-cache" class="block text-sm font-medium text-gray-700 mb-1">Cache Expiration (minutes)</label>
            <input 
              id="tmdb-cache" 
              v-model.number="tmdb.cache_expiration" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="60"
            />
          </div>
          
          <div class="form-group">
            <label for="tmdb-language" class="block text-sm font-medium text-gray-700 mb-1">Language</label>
            <input 
              id="tmdb-language" 
              v-model="tmdb.language" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="en"
            />
          </div>
          
          <div class="form-group">
            <label for="tmdb-region" class="block text-sm font-medium text-gray-700 mb-1">Region (optional)</label>
            <input 
              id="tmdb-region" 
              v-model="tmdb.region" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="US"
            />
          </div>
        </div>
      </div>
      
      <!-- AniDB Settings -->
      <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
        <h3 class="text-lg font-medium mb-3">AniDB API</h3>
        
        <div class="grid grid-cols-1 gap-4">
          <div class="form-group">
            <label for="anidb-username" class="block text-sm font-medium text-gray-700 mb-1">Username</label>
            <input 
              id="anidb-username" 
              v-model="anidb.username" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="Your AniDB username"
            />
          </div>
          
          <div class="form-group">
            <label for="anidb-password" class="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <div class="relative">
              <input 
                id="anidb-password" 
                :type="showPassword ? 'text' : 'password'" 
                v-model="anidb.password" 
                class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
                placeholder="Your AniDB password"
              />
              <button 
                type="button" 
                @click="showPassword = !showPassword" 
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-600 focus:outline-none"
              >
                <!-- Eye Icon (when password is hidden) -->
                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
                <!-- Eye Slash Icon (when password is visible) -->
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="form-group">
            <label for="anidb-client" class="block text-sm font-medium text-gray-700 mb-1">Client ID</label>
            <input 
              id="anidb-client" 
              v-model.number="anidb.client" 
              type="number" 
              min="1"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="1"
            />
          </div>
          
          <div class="form-group">
            <label for="anidb-language" class="block text-sm font-medium text-gray-700 mb-1">Language</label>
            <input 
              id="anidb-language" 
              v-model="anidb.language" 
              type="text" 
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="en"
            />
          </div>
          
          <div class="form-group">
            <label for="anidb-cache" class="block text-sm font-medium text-gray-700 mb-1">Cache Expiration (minutes)</label>
            <input 
              id="anidb-cache" 
              v-model.number="anidb.cache_expiration" 
              type="number" 
              min="0"
              class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
              placeholder="60"
            />
          </div>
        </div>
      </div>
      
      <!-- Submit Button -->
      <div class="flex justify-end">
        <button 
          type="submit" 
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          :disabled="saving"
        >
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
        <div class="toast toast-top toast-end w-64" v-if="success">
        <div class="alert alert-success shadow-lg w-64 flex items-center space-x-2">
          <!-- icon -->
          <svg xmlns="http://www.w3.org/2000/svg" 
              class="stroke-current h-6 w-6 flex-shrink-0" 
              fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" 
                  stroke-width="2" d="M5 13l4 4L19 7" />
          </svg>
          <!-- text -->
          <span>API settings saved!</span>
        </div>
      </div>
      <div class="toast toast-top toast-end w-64" v-if="error">
          <div class="alert alert-error shadow-lg w-64 flex items-center space-x-2">
            <div>
              <!-- icon -->
              <svg xmlns="http://www.w3.org/2000/svg" 
                  class="stroke-current h-6 w-6 flex-shrink-0" 
                  fill="none" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" 
                      stroke-width="2" d="M5 13l4 4L19 7" />
              </svg>
              <span>API settings NOT saved!</span>
            </div>
          </div>
        </div>
      </div>
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import api from '@/api/config.js';

export default {
  name: 'ApiSettings',
  
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const success = ref(false);
    const saving = ref(false);
    const connectionTesting = ref(false);
    const connectionStatus = ref(null);
    const showPassword = ref(false); // For password visibility toggle
    
    // For API integration
    
    // Form data
    const jellyfin = reactive({
      url: 'https://jellyfin.example.com',
      api_key: '',
      user_id: ''
    });
    
    const omdb = reactive({
      api_key: '',
      cache_expiration: 60
    });
    
    const tmdb = reactive({
      api_key: '',
      cache_expiration: 60,
      language: 'en',
      region: ''
    });
    
    const anidb = reactive({
      username: '',
      password: '',
      client: 1,
      language: 'en',
      cache_expiration: 60
    });
    
    // Load settings
    const loadSettings = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const res = await api.getConfig('settings.yaml');
        const config = res.data.config;
        
        if (config && config.api_keys) {
          // Load Jellyfin settings (first item in array)
          if (config.api_keys.Jellyfin && config.api_keys.Jellyfin.length > 0) {
            const jellyfinConfig = config.api_keys.Jellyfin[0];
            jellyfin.url = jellyfinConfig.url || '';
            jellyfin.api_key = jellyfinConfig.api_key || '';
            jellyfin.user_id = jellyfinConfig.user_id || '';
          }
          
          // Load OMDB settings (first item in array)
          if (config.api_keys.OMDB && config.api_keys.OMDB.length > 0) {
            const omdbConfig = config.api_keys.OMDB[0];
            omdb.api_key = omdbConfig.api_key || '';
            omdb.cache_expiration = omdbConfig.cache_expiration || 60;
          }
          
          // Load TMDB settings (first item in array)
          if (config.api_keys.TMDB && config.api_keys.TMDB.length > 0) {
            const tmdbConfig = config.api_keys.TMDB[0];
            tmdb.api_key = tmdbConfig.api_key || '';
            tmdb.cache_expiration = tmdbConfig.cache_expiration || 60;
            tmdb.language = tmdbConfig.language || 'en';
            tmdb.region = tmdbConfig.region || '';
          }
          
          // Load AniDB settings (has special structure with data across two array items)
          if (config.api_keys.aniDB && config.api_keys.aniDB.length > 0) {
            // Username is in first array item
            if (config.api_keys.aniDB[0]) {
              anidb.username = config.api_keys.aniDB[0].username || '';
            }
            
            // Password and other settings are in the second array item
            if (config.api_keys.aniDB.length > 1 && config.api_keys.aniDB[1]) {
              const aniDbConfig = config.api_keys.aniDB[1];
              anidb.password = aniDbConfig.password || '';
              anidb.client = aniDbConfig.client || 1;
              anidb.language = aniDbConfig.language || 'en';
              anidb.cache_expiration = aniDbConfig.cache_expiration || 60;
            }
          }
        }
      } catch (err) {
        error.value = err.response?.data?.error || err.message || 'Failed to load API settings';
      } finally {
        loading.value = false;
      }
    };
    
    // Save settings
    const saveSettings = async () => {
      saving.value = true;
      error.value = null;
      success.value = false;
      
      try {
        // Construct the settings object in the format expected by the backend
        const settingsObj = {
          api_keys: {
            Jellyfin: [
              {
                url: jellyfin.url,
                api_key: jellyfin.api_key,
                user_id: jellyfin.user_id
              }
            ],
            OMDB: [
              {
                api_key: omdb.api_key,
                cache_expiration: omdb.cache_expiration
              }
            ],
            TMDB: [
              {
                api_key: tmdb.api_key,
                cache_expiration: tmdb.cache_expiration,
                language: tmdb.language,
                region: tmdb.region || null
              }
            ],
            aniDB: [
              {
                username: anidb.username
              },
              {
                password: anidb.password,
                client: anidb.client,
                language: anidb.language,
                cache_expiration: anidb.cache_expiration
              }
            ]
          }
        };
        
        // Save settings to the backend
        await api.updateConfig('settings.yaml', settingsObj);
        success.value = true;
        setTimeout(() => success.value = false, 3000);
      } catch (err) {
        error.value = err.response?.data?.error || err.message || 'Failed to save API settings';
      } finally {
        saving.value = false;
      }
    };
    
    // Test Jellyfin connection
    const testJellyfinConnection = async () => {
      connectionTesting.value = true;
      connectionStatus.value = null;
      
      try {
        // Check for required fields
        if (!jellyfin.url || !jellyfin.api_key || !jellyfin.user_id) {
          connectionStatus.value = {
            success: false,
            message: 'Please fill in all Jellyfin fields'
          };
          connectionTesting.value = false;
          return;
        }
        
        // Make API call to backend to test connection using the api client
        const response = await api.testJellyfinConnection({
          url: jellyfin.url,
          api_key: jellyfin.api_key,
          user_id: jellyfin.user_id
        });

        // Access the data directly from the response
        const data = response.data;

        connectionStatus.value = {
          success: true,
          message: data.message || 'Connection successful!'
        };
        connectionTesting.value = false;
      } catch (err) {
        connectionStatus.value = {
          success: false,
          message: err.response?.data?.error || 'Connection failed'
        };
        connectionTesting.value = false;
      }
    };
    
    onMounted(() => {
      loadSettings();
    });
    
    return {
      loading,
      error,
      saving,
      connectionTesting,
      connectionStatus,
      jellyfin,
      omdb,
      tmdb,
      anidb,
      success,
      saveSettings,
      testJellyfinConnection,
      showPassword
    };
  }
};
</script>
