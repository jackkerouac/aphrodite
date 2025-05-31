<template>
  <div class="schedules p-4">
    <h1 class="text-2xl font-bold mb-6">Schedules</h1>
    
    <!-- Schedules Tabs -->
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
      <!-- Schedule Manager Tab -->
      <ScheduleManager 
        v-if="activeTab === 'manager'"
        @create-schedule="showCreateEditor"
        @edit-schedule="showEditEditor"
      />
      
      <!-- Schedule History Tab -->
      <ScheduleHistory v-if="activeTab === 'history'" />
      
      <!-- Schedule Editor (Create/Edit) -->
      <ScheduleEditor 
        v-if="activeTab === 'editor'"
        :edit-schedule="editingSchedule"
        @save="handleScheduleSave"
        @cancel="cancelEdit"
      />
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ScheduleManager from '../components/ScheduleManager.vue'
import ScheduleHistory from '../components/ScheduleHistory.vue'
import ScheduleEditor from '../components/ScheduleEditor.vue'

export default {
  name: 'SchedulesView',
  components: {
    ScheduleManager,
    ScheduleHistory,
    ScheduleEditor
  },
  
  setup() {
    const route = useRoute()
    const router = useRouter()
    
    // Tabs setup
    const tabs = [
      { id: 'manager', name: 'Schedules' },
      { id: 'history', name: 'History' },
      { id: 'editor', name: 'Editor' }
    ]
    
    const activeTab = ref('manager')
    const editingSchedule = ref(null)
    
    // Set active tab based on route query parameter
    onMounted(() => {
      if (route.query.tab && tabs.some(tab => tab.id === route.query.tab)) {
        activeTab.value = route.query.tab
      }
    })
    
    // Watch for route changes
    watch(
      () => route.query.tab,
      (newTab) => {
        if (newTab && tabs.some(tab => tab.id === newTab)) {
          activeTab.value = newTab
        }
      }
    )
    
    // Watch for tab changes to update URL
    watch(activeTab, (newTab) => {
      router.push({ query: { ...route.query, tab: newTab } })
    })
    
    // Methods
    const showCreateEditor = () => {
      editingSchedule.value = null
      activeTab.value = 'editor'
    }
    
    const showEditEditor = (schedule) => {
      editingSchedule.value = schedule
      activeTab.value = 'editor'
    }
    
    const handleScheduleSave = () => {
      // Reset editor and go back to manager
      editingSchedule.value = null
      activeTab.value = 'manager'
    }
    
    const cancelEdit = () => {
      // Reset editor and go back to manager
      editingSchedule.value = null
      activeTab.value = 'manager'
    }
    
    return {
      tabs,
      activeTab,
      editingSchedule,
      showCreateEditor,
      showEditEditor,
      handleScheduleSave,
      cancelEdit
    }
  }
}
</script>
