<template>
  <div class="api-settings">
    <h2 class="text-xl font-bold mb-4">API Settings</h2>
    
    <form @submit.prevent="saveSettings" class="space-y-6">
      <!-- Jellyfin Settings -->
      <JellyfinSettings
        :model-value="jellyfin"
        @update:model-value="(newValue) => { console.log('DEBUG: Manual v-model update:', newValue); Object.assign(jellyfin, newValue); }"
        :testing="connectionTesting"
        :status="connectionStatus"
        @test="testJellyfinConnection"
      />
      
      <!-- OMDB Settings -->
      <OmdbSettings
        :model-value="omdb"
        @update:model-value="(newValue) => { console.log('DEBUG: Manual OMDB v-model update:', newValue); Object.assign(omdb, newValue); }"
        :testing="omdbTesting"
        :status="omdbStatus"
        @test="testOmdbConnection"
      />
      
      <!-- TMDB Settings -->
      <TmdbSettings
        :model-value="tmdb"
        @update:model-value="(newValue) => { console.log('DEBUG: Manual TMDB v-model update:', newValue); Object.assign(tmdb, newValue); }"
        :testing="tmdbTesting"
        :status="tmdbStatus"
        @test="testTmdbConnection"
      />
      
      <!-- MDBList Settings -->
      <MdblistSettings
        :model-value="mdblist"
        @update:model-value="(newValue) => { console.log('DEBUG: Manual MDBList v-model update:', newValue); Object.assign(mdblist, newValue); }"
        :testing="mdblistTesting"
        :status="mdblistStatus"
        @test="testMdblistConnection"
      />
      
      <!-- AniDB Settings -->
      <AnidbSettings
        :model-value="anidb"
        @update:model-value="(newValue) => { console.log('DEBUG: Manual AniDB v-model update:', newValue); Object.assign(anidb, newValue); }"
        :testing="anidbTesting"
        :status="anidbStatus"
        @test="testAnidbConnection"
      />
      
      <!-- Submit Button -->
      <div class="flex justify-end">
        <button 
          type="submit" 
          class="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          :disabled="saving"
        >
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
        
        <!-- Success Toast -->
        <div class="toast toast-top toast-end w-64" v-if="success">
          <div class="alert alert-success shadow-lg w-64 flex items-center space-x-2">
            <svg xmlns="http://www.w3.org/2000/svg" 
                class="stroke-current h-6 w-6 flex-shrink-0" 
                fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" 
                    stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
            <span>API settings saved!</span>
          </div>
        </div>
        
        <!-- Error Toast -->
        <div class="toast toast-top toast-end w-64" v-if="error">
          <div class="alert alert-error shadow-lg w-64 flex items-center space-x-2">
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
    </form>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue';
import api from '@/api/config.js';
import JellyfinSettings from './api/JellyfinSettings.vue';
import OmdbSettings from './api/OmdbSettings.vue';
import TmdbSettings from './api/TmdbSettings.vue';
import MdblistSettings from './api/MdblistSettings.vue';
import AnidbSettings from './api/AnidbSettings.vue';

export default {
  name: 'ApiSettings',
  components: {
    JellyfinSettings,
    OmdbSettings,
    TmdbSettings,
    MdblistSettings,
    AnidbSettings
  },
  
  setup() {
    const loading = ref(false);
    const error = ref(null);
    const success = ref(false);
    const saving = ref(false);
    
    // Connection testing states for each API
    const connectionTesting = ref(false);
    const connectionStatus = ref(null);
    const omdbTesting = ref(false);
    const omdbStatus = ref(null);
    const tmdbTesting = ref(false);
    const tmdbStatus = ref(null);
    const mdblistTesting = ref(false);
    const mdblistStatus = ref(null);
    const anidbTesting = ref(false);
    const anidbStatus = ref(null);
    
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
      version: 1,
      client_name: '',
      language: 'en',
      cache_expiration: 60
    });
    
    const mdblist = reactive({
      api_key: '',
      cache_expiration: 60
    });
    
    // Load settings
    const loadSettings = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        console.log('DEBUG: Loading settings from API...');
        const res = await api.getConfig('settings.yaml');
        const config = res.data.config;
        console.log('DEBUG: Received config from API:', config);
        
        if (config && config.api_keys) {
          // Load Jellyfin settings
          if (config.api_keys.Jellyfin && config.api_keys.Jellyfin.length > 0) {
            const jellyfinConfig = config.api_keys.Jellyfin[0];
            console.log('DEBUG: Loading Jellyfin config:', jellyfinConfig);
            console.log('DEBUG: Current jellyfin reactive object before update:', jellyfin);
            
            // Update properties directly instead of using Object.assign
            jellyfin.url = jellyfinConfig.url || '';
            jellyfin.api_key = jellyfinConfig.api_key || '';
            jellyfin.user_id = jellyfinConfig.user_id || '';
            
            console.log('DEBUG: Current jellyfin reactive object after update:', jellyfin);
          }
          
          // Load OMDB settings
          if (config.api_keys.OMDB && config.api_keys.OMDB.length > 0) {
            const omdbConfig = config.api_keys.OMDB[0];
            console.log('DEBUG: Loading OMDB config:', omdbConfig);
            
            // Update properties directly instead of using Object.assign
            omdb.api_key = omdbConfig.api_key || '';
            omdb.cache_expiration = omdbConfig.cache_expiration || 60;
            
            console.log('DEBUG: Updated OMDB object:', omdb);
          }
          
          // Load TMDB settings
          if (config.api_keys.TMDB && config.api_keys.TMDB.length > 0) {
            const tmdbConfig = config.api_keys.TMDB[0];
            console.log('DEBUG: Loading TMDB config:', tmdbConfig);
            
            // Update properties directly instead of using Object.assign
            tmdb.api_key = tmdbConfig.api_key || '';
            tmdb.cache_expiration = tmdbConfig.cache_expiration || 60;
            tmdb.language = tmdbConfig.language || 'en';
            tmdb.region = tmdbConfig.region || '';
            
            console.log('DEBUG: Updated TMDB object:', tmdb);
          }
          
          // Load AniDB settings
          if (config.api_keys.aniDB) {
            const anidbConfig = config.api_keys.aniDB;
            console.log('DEBUG: Loading AniDB config:', anidbConfig);
            
            if (Array.isArray(anidbConfig)) {
              if (anidbConfig.length > 0 && anidbConfig[0]) {
                anidb.username = anidbConfig[0].username || '';
              }
              
              if (anidbConfig.length > 1 && anidbConfig[1]) {
                const secondItem = anidbConfig[1];
                anidb.password = secondItem.password || '';
                anidb.version = secondItem.version || 1;
                anidb.client_name = secondItem.client_name || '';
                anidb.language = secondItem.language || 'en';
                anidb.cache_expiration = secondItem.cache_expiration || 60;
              }
            } else if (typeof anidbConfig === 'object') {
              anidb.username = anidbConfig.username || '';
              anidb.password = anidbConfig.password || '';
              anidb.version = anidbConfig.version || 1;
              anidb.client_name = anidbConfig.client_name || '';
              anidb.language = anidbConfig.language || 'en';
              anidb.cache_expiration = anidbConfig.cache_expiration || 60;
            }
            
            console.log('DEBUG: Updated AniDB object:', anidb);
          }
          
          // Load MDBList settings
          if (config.api_keys.MDBList && config.api_keys.MDBList.length > 0) {
            const mdblistConfig = config.api_keys.MDBList[0];
            console.log('DEBUG: Loading MDBList config:', mdblistConfig);
            
            // Update properties directly instead of using Object.assign
            mdblist.api_key = mdblistConfig.api_key || '';
            mdblist.cache_expiration = mdblistConfig.cache_expiration || 60;
            
            console.log('DEBUG: Updated MDBList object:', mdblist);
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
      
      console.log('DEBUG: Saving settings...');
      console.log('DEBUG: Current jellyfin reactive object before save:', jellyfin);
      
      try {
        const settingsObj = {
          api_keys: {
            Jellyfin: [{
              url: jellyfin.url,
              api_key: jellyfin.api_key,
              user_id: jellyfin.user_id
            }],
            OMDB: [{
              api_key: omdb.api_key,
              cache_expiration: omdb.cache_expiration
            }],
            TMDB: [{
              api_key: tmdb.api_key,
              cache_expiration: tmdb.cache_expiration,
              language: tmdb.language,
              region: tmdb.region || null
            }],
            aniDB: [
              { username: anidb.username },
              {
                password: anidb.password,
                version: anidb.version,
                client_name: anidb.client_name,
                language: anidb.language,
                cache_expiration: anidb.cache_expiration
              }
            ],
            MDBList: [{
              api_key: mdblist.api_key,
              cache_expiration: mdblist.cache_expiration
            }]
          }
        };
        
        console.log('DEBUG: Settings object to be sent:', settingsObj);
        console.log('DEBUG: Jellyfin URL in settings object:', settingsObj.api_keys.Jellyfin[0].url);
        
        await api.updateConfig('settings.yaml', settingsObj);
        success.value = true;
        setTimeout(() => success.value = false, 3000);
      } catch (err) {
        error.value = err.response?.data?.error || err.message || 'Failed to save API settings';
      } finally {
        saving.value = false;
      }
    };
    
    // Test connection functions
    const testJellyfinConnection = async () => {
      connectionTesting.value = true;
      connectionStatus.value = null;
      
      try {
        if (!jellyfin.url || !jellyfin.api_key || !jellyfin.user_id) {
          connectionStatus.value = {
            success: false,
            message: 'Please fill in all Jellyfin fields'
          };
          return;
        }
        
        const response = await api.testJellyfinConnection({
          url: jellyfin.url,
          api_key: jellyfin.api_key,
          user_id: jellyfin.user_id
        });

        connectionStatus.value = {
          success: true,
          message: response.data.message || 'Connection successful!'
        };
        
        // Auto-save settings when connection test succeeds
        try {
          console.log('DEBUG: Connection test successful, auto-saving settings...');
          await saveSettings();
          
          // Update the success message to indicate auto-save
          connectionStatus.value = {
            success: true,
            message: (response.data.message || 'Connection successful!') + ' - Settings saved automatically!'
          };
        } catch (saveError) {
          console.error('DEBUG: Auto-save failed:', saveError);
          connectionStatus.value = {
            success: true,
            message: (response.data.message || 'Connection successful!') + ' - Warning: Auto-save failed, please save manually.'
          };
        }
      } catch (err) {
        connectionStatus.value = {
          success: false,
          message: err.response?.data?.error || 'Connection failed'
        };
      } finally {
        connectionTesting.value = false;
      }
    };
    
    const testOmdbConnection = async () => {
      omdbTesting.value = true;
      omdbStatus.value = null;
      
      try {
        if (!omdb.api_key) {
          omdbStatus.value = {
            success: false,
            message: 'Please enter an OMDB API key'
          };
          return;
        }
        
        const response = await api.testConnection('omdb', {
          api_key: omdb.api_key
        });

        omdbStatus.value = {
          success: true,
          message: response.data.message || 'Connection successful!'
        };
      } catch (err) {
        omdbStatus.value = {
          success: false,
          message: err.response?.data?.error || 'Connection failed'
        };
      } finally {
        omdbTesting.value = false;
      }
    };
    
    const testTmdbConnection = async () => {
      tmdbTesting.value = true;
      tmdbStatus.value = null;
      
      try {
        if (!tmdb.api_key) {
          tmdbStatus.value = {
            success: false,
            message: 'Please enter a TMDB API key'
          };
          return;
        }
        
        const response = await api.testConnection('tmdb', {
          api_key: tmdb.api_key,
          language: tmdb.language,
          region: tmdb.region
        });

        tmdbStatus.value = {
          success: true,
          message: response.data.message || 'Connection successful!'
        };
      } catch (err) {
        tmdbStatus.value = {
          success: false,
          message: err.response?.data?.error || 'Connection failed'
        };
      } finally {
        tmdbTesting.value = false;
      }
    };
    
    const testMdblistConnection = async () => {
      mdblistTesting.value = true;
      mdblistStatus.value = null;
      
      try {
        if (!mdblist.api_key) {
          mdblistStatus.value = {
            success: false,
            message: 'Please enter an MDBList API key'
          };
          return;
        }
        
        const response = await api.testConnection('mdblist', {
          api_key: mdblist.api_key
        });

        mdblistStatus.value = {
          success: true,
          message: response.data.message || 'Connection successful!'
        };
      } catch (err) {
        mdblistStatus.value = {
          success: false,
          message: err.response?.data?.error || 'Connection failed'
        };
      } finally {
        mdblistTesting.value = false;
      }
    };
    
    const testAnidbConnection = async () => {
      anidbTesting.value = true;
      anidbStatus.value = null;
      
      try {
        if (!anidb.username || !anidb.password) {
          anidbStatus.value = {
            success: false,
            message: 'Please enter AniDB username and password'
          };
          return;
        }
        
        const response = await api.testConnection('anidb', {
          username: anidb.username,
          password: anidb.password,
          version: anidb.version,
          client_name: anidb.client_name,
          language: anidb.language
        });

        anidbStatus.value = {
          success: true,
          message: response.data.message || 'Connection successful!'
        };
      } catch (err) {
        anidbStatus.value = {
          success: false,
          message: err.response?.data?.error || 'Connection failed'
        };
      } finally {
        anidbTesting.value = false;
      }
    };
    
    onMounted(() => {
      loadSettings();
    });
    
    // Watch for changes to jellyfin object
    watch(jellyfin, (newValue, oldValue) => {
      console.log('DEBUG: jellyfin object changed!');
      console.log('DEBUG: Old value:', oldValue);
      console.log('DEBUG: New value:', newValue);
    }, { deep: true });
    
    return {
      loading,
      error,
      saving,
      success,
      connectionTesting,
      connectionStatus,
      omdbTesting,
      omdbStatus,
      tmdbTesting,
      tmdbStatus,
      mdblistTesting,
      mdblistStatus,
      anidbTesting,
      anidbStatus,
      jellyfin,
      omdb,
      tmdb,
      anidb,
      mdblist,
      saveSettings,
      testJellyfinConnection,
      testOmdbConnection,
      testTmdbConnection,
      testMdblistConnection,
      testAnidbConnection
    };
  }
};
</script>
