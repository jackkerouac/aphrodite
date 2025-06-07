<template>
  <div v-if="isVisible" class="modal modal-open">
    <div class="modal-box w-11/12 max-w-3xl">
      <!-- Modal Header -->
      <div class="flex justify-between items-center mb-6">
        <h3 class="font-bold text-lg">Badge Processing Progress</h3>
        <button 
          class="btn btn-sm btn-circle btn-ghost" 
          @click="handleClose"
        >
          ✕
        </button>
      </div>

      <!-- Overall Progress -->
      <div class="mb-6">
        <div class="flex justify-between items-center mb-2">
          <span class="text-sm font-medium">Overall Progress</span>
          <span class="text-sm">{{ completedJobs }} / {{ totalJobs }} completed</span>
        </div>
        <progress 
          class="progress progress-primary w-full" 
          :value="progressPercentage" 
          max="100"
        ></progress>
        <div class="text-xs text-center mt-1">{{ Math.round(progressPercentage) }}%</div>
      </div>

      <!-- Status Summary -->
      <div class="grid grid-cols-3 gap-4 mb-6">
        <div class="stat bg-base-200 rounded-lg">
          <div class="stat-title text-xs">Completed</div>
          <div class="stat-value text-lg text-success">{{ successCount }}</div>
        </div>
        <div class="stat bg-base-200 rounded-lg">
          <div class="stat-title text-xs">Failed</div>
          <div class="stat-value text-lg text-error">{{ failedCount }}</div>
        </div>
        <div class="stat bg-base-200 rounded-lg">
          <div class="stat-title text-xs">Processing</div>
          <div class="stat-value text-lg text-warning">{{ runningCount }}</div>
        </div>
      </div>

      <!-- Individual Job Status -->
      <div class="mb-6">
        <h4 class="font-semibold mb-3">Individual Job Status</h4>
        <div class="max-h-60 overflow-y-auto bg-base-200 rounded-lg p-3">
          <div class="space-y-2">
            <div 
              v-for="job in jobStatuses" 
              :key="job.item_id"
              class="flex items-center justify-between p-2 bg-base-100 rounded"
            >
              <div class="flex items-center gap-3">
                <!-- Status Icon -->
                <div class="flex-shrink-0">
                  <div v-if="job.status === 'success'" class="w-4 h-4 rounded-full bg-success flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-success-content" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div v-else-if="job.status === 'failed'" class="w-4 h-4 rounded-full bg-error flex items-center justify-center">
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 text-error-content" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <div v-else class="loading loading-spinner loading-xs"></div>
                </div>
                
                <!-- Item Info -->
                <div class="min-w-0 flex-1">
                  <div class="text-sm font-medium truncate">{{ job.item_name || job.item_id }}</div>
                  <div class="text-xs opacity-60">{{ formatJobStatus(job.status) }}</div>
                </div>
              </div>
              
              <!-- Error Details -->
              <div v-if="job.status === 'failed' && job.error" class="text-xs text-error max-w-xs truncate" :title="job.error">
                {{ job.error }}
              </div>
            </div>
            
            <!-- Loading placeholder if no jobs yet -->
            <div v-if="jobStatuses.length === 0" class="text-center py-4 text-sm opacity-60">
              Loading job details...
            </div>
          </div>
        </div>
      </div>

      <!-- Completion Message -->
      <div v-if="isComplete" class="alert" :class="hasErrors ? 'alert-warning' : 'alert-success'">
        <svg v-if="!hasErrors" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <div>
          <div class="font-medium">
            {{ hasErrors ? 'Processing completed with some errors' : 'All posters processed successfully!' }}
          </div>
          <div class="text-sm opacity-80">
            {{ successCount }} successful, {{ failedCount }} failed
          </div>
        </div>
      </div>

      <!-- Modal Actions -->
      <div class="modal-action">
        <button 
          v-if="!isComplete"
          class="btn btn-ghost" 
          @click="handleClose"
        >
          Continue in Background
        </button>
        <button 
          v-if="isComplete"
          class="btn btn-primary" 
          @click="handleClose"
        >
          Close
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onUnmounted } from 'vue'
import api from '@/api'

export default {
  name: 'GlobalProgressModal',
  props: {
    batchId: {
      type: String,
      default: null
    },
    isVisible: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  setup(props, { emit }) {
    const jobStatuses = ref([])
    const totalJobs = ref(0)
    const completedJobs = ref(0)
    const isComplete = ref(false)
    const pollInterval = ref(null)
    
    // Computed properties
    const progressPercentage = computed(() => {
      if (totalJobs.value === 0) return 0
      return (completedJobs.value / totalJobs.value) * 100
    })
    
    const successCount = computed(() => {
      return jobStatuses.value.filter(job => job.status === 'success').length
    })
    
    const failedCount = computed(() => {
      return jobStatuses.value.filter(job => job.status === 'failed').length
    })
    
    const runningCount = computed(() => {
      return jobStatuses.value.filter(job => ['queued', 'running'].includes(job.status)).length
    })
    
    const hasErrors = computed(() => {
      return failedCount.value > 0
    })
    
    // Methods
    const fetchBatchStatus = async () => {
      if (!props.batchId) return
      
      try {
        const response = await api.get(`/api/poster-manager/bulk/status/${props.batchId}`)
        const data = response.data
        
        if (data.success) {
          jobStatuses.value = data.jobs || []
          totalJobs.value = data.total || jobStatuses.value.length
          completedJobs.value = data.completed || jobStatuses.value.filter(job => 
            ['success', 'failed'].includes(job.status)
          ).length
          isComplete.value = data.is_complete || completedJobs.value === totalJobs.value
          
          // Stop polling if complete
          if (isComplete.value && pollInterval.value) {
            clearInterval(pollInterval.value)
            pollInterval.value = null
          }
        }
      } catch (error) {
        console.error('Error fetching batch status:', error)
      }
    }
    
    const startPolling = () => {
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
      }
      pollInterval.value = setInterval(fetchBatchStatus, 2000) // Poll every 2 seconds
    }
    
    const stopPolling = () => {
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
        pollInterval.value = null
      }
    }
    
    const formatJobStatus = (status) => {
      switch (status) {
        case 'queued': return 'Waiting to start...'
        case 'running': return 'Processing...'
        case 'success': return 'Completed successfully'
        case 'failed': return 'Failed'
        default: return status
      }
    }
    
    const handleClose = () => {
      stopPolling()
      emit('close')
    }
    
    // Watch for changes in visibility and batchId
    watch(() => props.isVisible, (newVisible) => {
      if (newVisible && props.batchId) {
        fetchBatchStatus()
        startPolling()
      } else {
        stopPolling()
      }
    })
    
    watch(() => props.batchId, (newBatchId) => {
      if (newBatchId && props.isVisible) {
        fetchBatchStatus()
        startPolling()
      } else {
        stopPolling()
      }
    })
    
    // Cleanup
    onUnmounted(() => {
      stopPolling()
    })
    
    return {
      jobStatuses,
      totalJobs,
      completedJobs,
      isComplete,
      progressPercentage,
      successCount,
      failedCount,
      runningCount,
      hasErrors,
      formatJobStatus,
      handleClose
    }
  }
}
</script>
