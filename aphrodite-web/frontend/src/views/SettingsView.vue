<template>
  <div class="settings p-4">
    <h1 class="text-2xl font-bold mb-6">Settings</h1>
    
    <!-- Global Loading Spinner -->
    <div v-if="isLoading" class="flex items-center justify-center min-h-96">
      <div class="text-center">
        <div class="loading loading-spinner loading-lg text-blue-600 mb-4"></div>
        <p class="text-gray-600">Loading settings...</p>
        <div class="text-sm text-gray-500 mt-2">
          <div v-if="loadingStatus.api" class="flex items-center justify-center mb-1">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            API Settings
          </div>
          <div v-else class="flex items-center justify-center mb-1">
            <div class="loading loading-spinner loading-xs mr-2"></div>
            API Settings
          </div>
          
          <div v-if="loadingStatus.audio" class="flex items-center justify-center mb-1">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            Audio Settings
          </div>
          <div v-else class="flex items-center justify-center mb-1">
            <div class="loading loading-spinner loading-xs mr-2"></div>
            Audio Settings
          </div>
          
          <div v-if="loadingStatus.resolution" class="flex items-center justify-center mb-1">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            Resolution Settings
          </div>
          <div v-else class="flex items-center justify-center mb-1">
            <div class="loading loading-spinner loading-xs mr-2"></div>
            Resolution Settings
          </div>
          
          <div v-if="loadingStatus.review" class="flex items-center justify-center mb-1">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            Review Settings
          </div>
          <div v-else class="flex items-center justify-center mb-1">
            <div class="loading loading-spinner loading-xs mr-2"></div>
            Review Settings
          </div>
          
          <div v-if="loadingStatus.awards" class="flex items-center justify-center mb-1">
            <svg class="w-4 h-4 mr-2 text-green-500" fill="currentColor" viewBox="0 0 20 20">
              <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path>
            </svg>
            Awards Settings
          </div>
          <div v-else class="flex items-center justify-center mb-1">
            <div class="loading loading-spinner loading-xs mr-2"></div>
            Awards Settings
          </div>
        </div>
      </div>
    </div>
    
    <!-- Main Content - Hidden during loading -->
    <div v-else>
      <!-- Settings Tabs -->
      <div class="tabs tabs-boxed mb-6">
        <a 
          v-for="tab in tabs" 
          :key="tab.id"
          class="tab" 
          :class="{ 'tab-active': activeTab === tab.id }"
          @click="activeTab = tab.id"
        >
          {{ tab.name }}
        </a>
      </div>
      
      <!-- Tab Content -->
      <div class="bg-white rounded-lg shadow p-6">
        <!-- API Settings Tab -->
        <ApiSettings v-if="activeTab === 'api'" />
        
        <!-- Audio Badge Settings Tab -->
        <AudioSettings v-if="activeTab === 'audio'" />
        
        <!-- Resolution Badge Settings Tab -->
        <ResolutionSettings v-if="activeTab === 'resolution'" />
        
        <!-- Review Badge Settings Tab -->
        <ReviewSettings v-if="activeTab === 'review'" />
        
        <!-- Awards Badge Settings Tab -->
        <AwardsSettings v-if="activeTab === 'awards'" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import api from '@/api/config.js';
import ApiSettings from '../components/settings/ApiSettings.vue';
import AudioSettings from '../components/settings/AudioSettings.vue';
import ResolutionSettings from '../components/settings/ResolutionSettings.vue';
import ReviewSettings from '../components/settings/ReviewSettings.vue';
import AwardsSettings from '../components/settings/AwardsSettings.vue';

export default {
  name: 'SettingsView',
  components: {
    ApiSettings,
    AudioSettings,
    ResolutionSettings,
    ReviewSettings,
    AwardsSettings
  },
  
  setup() {
    const route = useRoute();
    
    // Tabs setup
    const tabs = [
      { id: 'api', name: 'API' },
      { id: 'audio', name: 'Audio' },
      { id: 'resolution', name: 'Resolution' },
      { id: 'review', name: 'Review' },
      { id: 'awards', name: 'Awards' }
    ];
    
    const activeTab = ref('api');
    const isLoading = ref(true);
    
    // Loading status for each settings type
    const loadingStatus = reactive({
      api: false,
      audio: false,
      resolution: false,
      review: false,
      awards: false
    });
    
    // Configuration files to check
    const configFiles = [
      { file: 'settings.yaml', key: 'api', name: 'API Settings' },
      { file: 'badge_settings_audio.yml', key: 'audio', name: 'Audio Settings' },
      { file: 'badge_settings_resolution.yml', key: 'resolution', name: 'Resolution Settings' },
      { file: 'badge_settings_review.yml', key: 'review', name: 'Review Settings' },
      { file: 'badge_settings_awards.yml', key: 'awards', name: 'Awards Settings' }
    ];
    
    // Check if all configuration files are accessible
    const checkAllConfigs = async () => {
      isLoading.value = true;
      
      try {
        // First, get the list of available config files
        const configFilesResponse = await api.getConfigFiles();
        const availableFiles = configFilesResponse.data.config_files || [];
        
        console.log('Available config files:', availableFiles);
        
        // Check each configuration file
        const checkPromises = configFiles.map(async ({ file, key, name }) => {
          try {
            if (availableFiles.includes(file)) {
              console.log(`Checking ${name}...`);
              // Just verify we can access the config, don't load the full content
              await api.getConfig(file);
              loadingStatus[key] = true;
              console.log(`✓ ${name} accessible`);
            } else {
              console.warn(`${name} not found, but that's ok`);
              loadingStatus[key] = true; // Mark as complete even if missing
            }
          } catch (error) {
            console.error(`Error checking ${name}:`, error);
            loadingStatus[key] = true; // Mark as complete even on error
          }
        });
        
        // Wait for all checks to complete
        await Promise.all(checkPromises);
        
        console.log('All configuration checks completed');
        
      } catch (error) {
        console.error('Error checking configuration files:', error);
        // Set all as loaded even on error so the interface shows
        Object.keys(loadingStatus).forEach(key => {
          loadingStatus[key] = true;
        });
      } finally {
        // Add a small delay to show the loading completion
        setTimeout(() => {
          isLoading.value = false;
        }, 300);
      }
    };
    
    // Set active tab based on route query parameter
    onMounted(() => {
      // Check all configurations when the component mounts
      checkAllConfigs();
      
      if (route.query.tab && tabs.some(tab => tab.id === route.query.tab)) {
        activeTab.value = route.query.tab;
      }
    });
    
    // Watch for route changes
    watch(
      () => route.query.tab,
      (newTab) => {
        if (newTab && tabs.some(tab => tab.id === newTab)) {
          activeTab.value = newTab;
        }
      }
    );
    
    return {
      tabs,
      activeTab,
      isLoading,
      loadingStatus
    };
  }
};
</script>
