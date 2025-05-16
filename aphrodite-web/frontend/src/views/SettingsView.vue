<template>
  <div class="settings p-4">
    <h1 class="text-2xl font-bold mb-6">Settings</h1>
    
    <!-- Settings Tabs -->
    <div class="mb-6 border-b border-gray-200">
      <ul class="flex flex-wrap -mb-px">
        <li class="mr-2" v-for="tab in tabs" :key="tab.id">
          <a 
            href="#"
            @click.prevent="activeTab = tab.id"
            :class="['inline-block py-2 px-4 border-b-2 font-medium text-sm', 
                   activeTab === tab.id ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-gray-600 hover:border-gray-300']"
          >
            {{ tab.name }}
          </a>
        </li>
      </ul>
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
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import ApiSettings from '../components/settings/ApiSettings.vue';
import AudioSettings from '../components/settings/AudioSettings.vue';
import ResolutionSettings from '../components/settings/ResolutionSettings.vue';
import ReviewSettings from '../components/settings/ReviewSettings.vue';

export default {
  name: 'SettingsView',
  components: {
    ApiSettings,
    AudioSettings,
    ResolutionSettings,
    ReviewSettings
  },
  
  setup() {
    const route = useRoute();
    
    // Tabs setup
    const tabs = [
      { id: 'api', name: 'API' },
      { id: 'audio', name: 'Audio' },
      { id: 'resolution', name: 'Resolution' },
      { id: 'review', name: 'Review' }
    ];
    
    const activeTab = ref('api');
    
    // Set active tab based on route query parameter
    onMounted(() => {
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
      activeTab
    };
  }
};
</script>
