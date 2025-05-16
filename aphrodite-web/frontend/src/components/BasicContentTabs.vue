<template>
  <div style="border: 10px solid green; padding: 10px; margin-top: 20px; background-color: #f0f0f0;">
    <h2 style="font-size: 20px; font-weight: bold; text-align: center; margin-bottom: 10px;">BASIC TABS COMPONENT</h2>
    
    <div style="display: flex; margin-bottom: 10px; border-bottom: 2px solid #ccc;">
      <button 
        v-for="tab in tabs" 
        :key="tab.id"
        @click="currentTab = tab.id"
        :style="{ 
          padding: '8px 16px', 
          marginRight: '8px',
          backgroundColor: currentTab === tab.id ? '#4CAF50' : '#ddd',
          color: currentTab === tab.id ? 'white' : 'black',
          border: 'none',
          borderTopLeftRadius: '4px',
          borderTopRightRadius: '4px',
          cursor: 'pointer'
        }"
      >
        {{ tab.name }}
      </button>
    </div>
    
    <div style="padding: 16px; border: 3px solid #000; background-color: white; min-height: 150px;">
      <!-- API Content -->
      <div v-if="currentTab === 'api'" style="background-color: lightgreen; padding: 20px; border: 2px solid darkgreen;">
        <h3 style="font-size: 18px; font-weight: bold; text-align: center;">API Settings</h3>
        <p>This is where API settings would go.</p>
      </div>
      
      <!-- Audio Content -->
      <div v-if="currentTab === 'audio'" style="background-color: lightblue; padding: 20px; border: 2px solid darkblue;">
        <h3 style="font-size: 18px; font-weight: bold; text-align: center;">Audio Settings</h3>
        <p>This is where Audio settings would go.</p>
      </div>
      
      <!-- Resolution Content -->
      <div v-if="currentTab === 'resolution'" style="background-color: pink; padding: 20px; border: 2px solid darkred;">
        <h3 style="font-size: 18px; font-weight: bold; text-align: center;">Resolution Settings</h3>
        <p>This is where Resolution settings would go.</p>
      </div>
      
      <!-- Review Content -->
      <div v-if="currentTab === 'review'" style="background-color: lavender; padding: 20px; border: 2px solid purple;">
        <h3 style="font-size: 18px; font-weight: bold; text-align: center;">Review Settings</h3>
        <p>This is where Review settings would go.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';

export default {
  name: 'BasicContentTabs',
  
  props: {
    initialTab: {
      type: String,
      default: 'api'
    }
  },
  
  setup(props) {
    const tabs = [
      { id: 'api', name: 'API' },
      { id: 'audio', name: 'Audio' },
      { id: 'resolution', name: 'Resolution' },
      { id: 'review', name: 'Review' }
    ];
    
    const currentTab = ref(props.initialTab);
    
    return {
      tabs,
      currentTab
    };
  }
};
</script>
