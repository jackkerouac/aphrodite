<template>
  <div class="database">
    <h1 class="text-2xl font-bold mb-4">Database Analytics</h1>
    
    <div class="mb-6">
      <p class="mb-4">Comprehensive insights into your media processing history and performance</p>
      
      <div class="tabs tabs-boxed mb-6">
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'reports' }"
          @click="activeTab = 'reports'"
        >
          Processing Reports
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'items' }"
          @click="activeTab = 'items'"
        >
          Item Browser
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'reviews' }"
          @click="activeTab = 'reviews'"
        >
          Review Management
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'settings' }"
          @click="activeTab = 'settings'"
        >
          Settings Monitor
        </a>
      </div>
      
      <!-- Processing Reports Tab -->
      <div v-if="activeTab === 'reports'">
        <ProcessingReportsPanel />
      </div>
      
      <!-- Item Browser Tab -->
      <div v-if="activeTab === 'items'">
        <ItemBrowserPanel />
      </div>
      
      <!-- Review Management Tab -->
      <div v-if="activeTab === 'reviews'">
        <ReviewManagementPanel />
      </div>
      
      <!-- Settings Monitor Tab -->
      <div v-if="activeTab === 'settings'">
        <SettingsMonitorPanel />
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import ProcessingReportsPanel from '../components/database/ProcessingReportsPanel.vue';
import ItemBrowserPanel from '../components/database/ItemBrowserPanel.vue';
import ReviewManagementPanel from '../components/database/ReviewManagementPanel.vue';
import SettingsMonitorPanel from '../components/database/SettingsMonitorPanel.vue';

export default {
  name: 'DatabaseView',
  components: {
    ProcessingReportsPanel,
    ItemBrowserPanel,
    ReviewManagementPanel,
    SettingsMonitorPanel
  },
  setup() {
    const route = useRouter().currentRoute.value;
    const activeTab = ref('reports');
    
    // Handle route query parameters
    if (route.query.tab) {
      const validTabs = ['reports', 'items', 'reviews', 'settings'];
      if (validTabs.includes(route.query.tab)) {
        activeTab.value = route.query.tab;
      }
    }
    
    return {
      activeTab
    };
  }
}
</script>
