<template>
  <div class="card bg-base-100 shadow-xl mb-6">
    <div class="card-body">
      <h2 class="card-title text-2xl mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        System Details
      </h2>
      
      <div v-if="loading" class="text-center py-8">
        <span class="loading loading-spinner loading-lg"></span>
        <p class="mt-4">Loading system information...</p>
      </div>
      
      <div v-else class="space-y-4">
        <VersionInfo 
          :version="systemInfo.version" 
          :update-info="updateInfo"
          :checking-updates="checkingUpdates"
          @check-updates="checkForUpdates"
        />
        
        <ExecutionModeInfo :execution-mode="systemInfo.execution_mode" />
        
        <DatabaseSchemaInfo :schema-hash="systemInfo.database_schema_hash" />
        
        <UptimeInfo :uptime="systemInfo.uptime" />
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/api'
import VersionInfo from './VersionInfo.vue'
import ExecutionModeInfo from './ExecutionModeInfo.vue'
import DatabaseSchemaInfo from './DatabaseSchemaInfo.vue'
import UptimeInfo from './UptimeInfo.vue'

export default {
  name: 'SystemDetailsCard',
  components: {
    VersionInfo,
    ExecutionModeInfo,
    DatabaseSchemaInfo,
    UptimeInfo
  },
  setup() {
    const loading = ref(true)
    const systemInfo = ref({
      version: 'Unknown',
      execution_mode: 'Unknown',
      database_schema_hash: 'Unknown',
      uptime: 'Unknown'
    })
    const checkingUpdates = ref(false)
    const updateInfo = ref(null)
    
    const loadSystemInfo = async () => {
      try {
        loading.value = true
        const response = await api.get('/api/about/system-info')
        const data = response.data
        
        if (data.success) {
          systemInfo.value = {
            version: data.version || 'Unknown',
            execution_mode: data.execution_mode || 'Unknown',
            database_schema_hash: data.database_schema_hash || 'Unknown',
            uptime: data.uptime || 'Unknown'
          }
        }
      } catch (error) {
        console.error('Failed to load system info:', error)
      } finally {
        loading.value = false
      }
    }
    
    const checkForUpdates = async () => {
      try {
        checkingUpdates.value = true
        const response = await api.get('/api/about/check-updates')
        const data = response.data
        
        if (data.success) {
          updateInfo.value = data
          
          if (!data.update_available) {
            console.log('No updates available')
          }
        }
      } catch (error) {
        console.error('Failed to check for updates:', error)
      } finally {
        checkingUpdates.value = false
      }
    }
    
    onMounted(() => {
      loadSystemInfo()
    })
    
    return {
      loading,
      systemInfo,
      checkingUpdates,
      updateInfo,
      checkForUpdates
    }
  }
}
</script>
