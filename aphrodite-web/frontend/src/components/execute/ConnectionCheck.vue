<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">API Connection Check</h2>
      <p class="mb-4">Check connectivity to configured API services.</p>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div v-for="(service, index) in services" :key="index" class="card bg-base-200">
          <div class="card-body p-4">
            <div class="flex justify-between items-center">
              <h3 class="text-lg font-medium">{{ service.name }}</h3>
              <div class="flex items-center">
                <div v-if="service.status === 'checking'" class="loading loading-spinner loading-sm mr-2"></div>
                <span 
                  v-else-if="service.status" 
                  class="badge" 
                  :class="service.status === 'connected' ? 'badge-success' : 'badge-error'"
                >
                  {{ service.status }}
                </span>
                <span v-else class="badge badge-ghost">Not checked</span>
              </div>
            </div>
            <p class="text-sm mt-2">{{ service.description }}</p>
            <p v-if="service.error" class="text-sm text-error mt-2">{{ service.error }}</p>
          </div>
        </div>
      </div>
      
      <div class="card-actions justify-end">
        <button class="btn btn-primary" @click="checkAllConnections" :disabled="isChecking">
          <span v-if="isChecking" class="loading loading-spinner loading-sm mr-2"></span>
          Check All Connections
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import configApi from '@/api/config';

export default {
  name: 'ConnectionCheck',
  setup() {
    const isChecking = ref(false);
    
    const services = reactive([
      {
        name: 'Jellyfin',
        description: 'Check connection to Jellyfin server using configured API key',
        status: null,
        error: null
      },
      {
        name: 'OMDB',
        description: 'Check connection to OMDB API using configured API key',
        status: null,
        error: null
      },
      {
        name: 'TMDB',
        description: 'Check connection to TMDB API using configured API key',
        status: null,
        error: null
      },
      {
        name: 'MDBList',
        description: 'Check connection to MDBList API using configured API key',
        status: null,
        error: null
      },
      {
        name: 'AniDB',
        description: 'Check connection to AniDB using configured credentials',
        status: null,
        error: null
      }
    ]);
    
    // Function to check Jellyfin connection
    const checkJellyfinConnection = async (service) => {
      service.status = 'checking';
      service.error = null;

      try {
        // Get Jellyfin settings
        const configResponse = await configApi.getConfig('settings.yaml');
        const config = configResponse.data.config;

        // Check if Jellyfin settings exist and make sure config is defined
        if (!config || !config.api_keys || !config.api_keys.Jellyfin || !config.api_keys.Jellyfin[0]) {
          service.status = 'failed';
          service.error = 'Jellyfin settings not configured';
          console.warn('Jellyfin settings missing in config:', config);
          return;
        }

        const jellyfin = config.api_keys.Jellyfin[0];

        // Check if required fields are filled
        if (!jellyfin.url || !jellyfin.api_key || !jellyfin.user_id) {
          service.status = 'failed';
          service.error = 'Jellyfin settings incomplete';
          console.warn('Jellyfin settings incomplete:', jellyfin);
          return;
        }

        // Log the credentials being used
        console.log('Testing Jellyfin connection with:', {
          url: jellyfin.url,
          api_key: jellyfin.api_key.substring(0, 4) + '...',
          user_id: jellyfin.user_id.substring(0, 4) + '...'
        });

        // Use the correct API client to test the connection
        const response = await configApi.testJellyfinConnection({
          url: jellyfin.url,
          api_key: jellyfin.api_key,
          user_id: jellyfin.user_id
        });

        // Log the response
        console.log('Jellyfin connection test response:', response.data);

        // Access the data directly from the response
        if (response.data && response.data.success) {
          service.status = 'connected';
        } else {
          service.status = 'failed';
          service.error = (response.data && response.data.error) ? response.data.error : 'Connection failed';
        }
      } catch (err) {
        console.error('Error checking Jellyfin connection:', err);
        service.status = 'failed';
        service.error = err.response?.data?.error || 'Connection error';
      }
    };

    // Function to check a single API connection
    const checkConnection = async (service) => {
      if (service.name === 'Jellyfin') {
        await checkJellyfinConnection(service);
        return;
      }

      service.status = 'checking';
      service.error = null;
      
      try {
        // Get settings
        const configResponse = await configApi.getConfig('settings.yaml');
        const config = configResponse.data.config;
        
        // Log the config for debugging
        console.log(`${service.name} connection check - config:`, config);
        
        // Make sure config exists and has api_keys
        if (!config || !config.api_keys) {
          service.status = 'failed';
          service.error = 'Settings not configured properly';
          console.warn(`${service.name} - Settings not configured properly:`, config);
          return;
        }
        
        switch(service.name) {
          case 'OMDB':
            // Check if OMDB API key exists and test connection
            if (!config.api_keys.OMDB || !config.api_keys.OMDB[0] || !config.api_keys.OMDB[0].api_key) {
              service.status = 'failed';
              service.error = 'OMDB API key not configured';
              console.warn('OMDB API key not configured or invalid:', config.api_keys.OMDB);
            } else {
              // Test actual connection to OMDB
              console.log('Testing OMDB connection...');
              try {
                const testResponse = await configApi.testConnection('omdb', {
                  api_key: config.api_keys.OMDB[0].api_key
                });
                
                if (testResponse.data && testResponse.data.success) {
                  service.status = 'connected';
                } else {
                  service.status = 'failed';
                  service.error = testResponse.data?.error || 'OMDB connection test failed';
                }
              } catch (testError) {
                console.error('OMDB connection test error:', testError);
                service.status = 'failed';
                service.error = testError.response?.data?.error || 'OMDB connection test failed';
              }
            }
            break;
            
          case 'TMDB':
            // Check if TMDB API key exists and test connection
            if (!config.api_keys.TMDB || !config.api_keys.TMDB[0] || !config.api_keys.TMDB[0].api_key) {
              service.status = 'failed';
              service.error = 'TMDB API key not configured';
              console.warn('TMDB API key not configured or invalid:', config.api_keys.TMDB);
            } else {
              // Test actual connection to TMDB
              console.log('Testing TMDB connection...');
              try {
                const testResponse = await configApi.testConnection('tmdb', {
                  api_key: config.api_keys.TMDB[0].api_key,
                  language: config.api_keys.TMDB[0].language || 'en'
                });
                
                if (testResponse.data && testResponse.data.success) {
                  service.status = 'connected';
                } else {
                  service.status = 'failed';
                  service.error = testResponse.data?.error || 'TMDB connection test failed';
                }
              } catch (testError) {
                console.error('TMDB connection test error:', testError);
                service.status = 'failed';
                service.error = testError.response?.data?.error || 'TMDB connection test failed';
              }
            }
            break;
            
          case 'MDBList':
            // Check if MDBList API key exists and test connection
            if (!config.api_keys.MDBList || !config.api_keys.MDBList[0] || !config.api_keys.MDBList[0].api_key) {
              service.status = 'failed';
              service.error = 'MDBList API key not configured';
              console.warn('MDBList API key not configured or invalid:', config.api_keys.MDBList);
            } else {
              // Test actual connection to MDBList
              console.log('Testing MDBList connection...');
              try {
                const testResponse = await configApi.testConnection('mdblist', {
                  api_key: config.api_keys.MDBList[0].api_key
                });
                
                if (testResponse.data && testResponse.data.success) {
                  service.status = 'connected';
                } else {
                  service.status = 'failed';
                  service.error = testResponse.data?.error || 'MDBList connection test failed';
                }
              } catch (testError) {
                console.error('MDBList connection test error:', testError);
                service.status = 'failed';
                service.error = testError.response?.data?.error || 'MDBList connection test failed';
              }
            }
            break;
            
          case 'AniDB':
            // Use a block scope to contain these variables
            {
              // Check if aniDB config exists
              if (!config.api_keys.aniDB) {
                service.status = 'failed';
                service.error = 'AniDB credentials not configured';
                console.warn('AniDB credentials not configured - missing aniDB key');
                break;
              }
              
              const anidbConfig = config.api_keys.aniDB;
              console.log('AniDB config:', anidbConfig);
              
              let username = '';
              let password = '';
              let client_name = 'aphrodite';
              let version = 3;
              
              // Handle both array and object formats based on how the ConfigService processes it
              if (Array.isArray(anidbConfig)) {
                console.log('AniDB config is an array with length:', anidbConfig.length);
                // Find username and password in any of the array elements
                for (const item of anidbConfig) {
                  if (item && typeof item === 'object') {
                    if (item.username) username = item.username;
                    if (item.password) password = item.password;
                    if (item.client_name) client_name = item.client_name;
                    if (item.version) version = item.version;
                  }
                }
              } else if (typeof anidbConfig === 'object') {
                console.log('AniDB config is an object');
                username = anidbConfig.username || '';
                password = anidbConfig.password || '';
                client_name = anidbConfig.client_name || 'aphrodite';
                version = anidbConfig.version || 3;
              }
              
              console.log('AniDB credentials found - username exists:', !!username, 'password exists:', !!password);
              
              if (!username || !password) {
                service.status = 'failed';
                service.error = 'AniDB credentials incomplete';
                console.warn('AniDB credentials incomplete - missing username or password');
              } else {
                // Test actual connection to AniDB
                console.log('Testing AniDB connection...');
                try {
                  const testResponse = await configApi.testConnection('anidb', {
                    username: username,
                    password: password,
                    client_name: client_name,
                    version: version
                  });
                  
                  if (testResponse.data && testResponse.data.success) {
                    service.status = 'connected';
                  } else {
                    service.status = 'failed';
                    service.error = testResponse.data?.error || 'AniDB connection test failed';
                  }
                } catch (testError) {
                  console.error('AniDB connection test error:', testError);
                  service.status = 'failed';
                  service.error = testError.response?.data?.error || 'AniDB connection test failed';
                }
              }
            }
            break;
            
          default:
            service.status = 'failed';
            service.error = 'Unknown service';
            console.warn('Unknown service:', service.name);
            break;
        }
      } catch (error) {
        console.error(`Error checking ${service.name} connection:`, error);
        service.status = 'failed';
        service.error = 'Error loading settings';
      }
    };
    
    // Function to check all connections
    const checkAllConnections = async () => {
      console.log('Starting connection check for all services');
      isChecking.value = true;
      
      try {
        // Instead of using Promise.all which can mask errors,
        // check connections one by one for better debugging
        for (const service of services) {
          console.log(`Checking connection for ${service.name}...`);
          try {
            await checkConnection(service);
            console.log(`${service.name} connection check completed with status: ${service.status}`);
          } catch (error) {
            console.error(`Error during ${service.name} connection check:`, error);
            service.status = 'failed';
            service.error = 'Unexpected error';
          }
        }
      } finally {
        console.log('All connection checks completed');
        isChecking.value = false;
      }
    };
    
    return {
      services,
      isChecking,
      checkAllConnections
    };
  }
};
</script>
