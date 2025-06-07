<template>
  <div v-if="activeBatches.length > 0" class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Active Badge Processing
      </h2>
      
      <div class="space-y-3">
        <div v-for="batch in activeBatches" :key="batch.batch_id" class="border border-base-300 rounded-lg p-3">
          <div class="flex justify-between items-start mb-2">
            <div>
              <div class="font-medium text-sm">
                {{ batch.total_jobs }} poster{{ batch.total_jobs !== 1 ? 's' : '' }}
              </div>
              <div class="text-xs opacity-60">
                Badges: {{ batch.selected_badges.join(', ') }}
              </div>
            </div>
            <div class="text-right">
              <div class="text-sm">
                {{ batch.completed_jobs }}/{{ batch.total_jobs }}
              </div>
              <div class="text-xs opacity-60">
                {{ batch.is_complete ? 'Complete' : `${batch.active_jobs} active` }}
              </div>
            </div>
          </div>
          
          <!-- Progress Bar -->
          <progress 
            class="progress progress-primary w-full h-2 mb-2" 
            :value="batch.completed_jobs" 
            :max="batch.total_jobs"
          ></progress>
          
          <!-- Action Button -->
          <button 
            class="btn btn-xs btn-outline btn-primary w-full"
            @click="$emit('view-progress', batch.batch_id)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            View Progress
          </button>
        </div>
      </div>
      
      <!-- Summary -->
      <div class="flex justify-between items-center mt-3">
        <div class="stats stats-horizontal shadow bg-base-200 flex-1">
          <div class="stat py-2">
            <div class="stat-title text-xs">Total Batches</div>
            <div class="stat-value text-sm">{{ activeBatches.length }}</div>
          </div>
          <div class="stat py-2">
            <div class="stat-title text-xs">Active Jobs</div>
            <div class="stat-value text-sm text-warning">{{ totalActiveJobs }}</div>
          </div>
        </div>
        
        <!-- Clear Completed Button -->
        <button 
          v-if="hasCompletedBatches"
          class="btn btn-sm btn-outline btn-error ml-3"
          @click="showClearConfirmation"
          :disabled="isClearing"
          title="Clear all completed batches"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
          {{ isClearing ? 'Clearing...' : 'Clear Completed' }}
        </button>
      </div>
    </div>
  </div>
  
  <!-- Clear Confirmation Dialog -->
  <div v-if="showClearDialog" class="modal modal-open">
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Clear Completed Batches</h3>
      <p class="mb-4">Are you sure you want to clear {{ completedBatchCount }} completed batch{{ completedBatchCount !== 1 ? 'es' : '' }}?</p>
      <p class="text-sm opacity-70 mb-6">This will remove them from your dashboard. Any active processing jobs will remain.</p>
      
      <div class="modal-action">
        <button class="btn btn-ghost" @click="showClearDialog = false" :disabled="isClearing">Cancel</button>
        <button class="btn btn-error" @click="clearCompletedBatches" :disabled="isClearing">
          <span v-if="isClearing" class="loading loading-spinner loading-sm"></span>
          {{ isClearing ? 'Clearing...' : 'Clear Completed' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '@/api'

export default {
  name: 'ActiveBadgeJobs',
  emits: ['view-progress'],
  setup() {
    const activeBatches = ref([])
    const totalActiveJobs = ref(0)
    const pollInterval = ref(null)
    const showClearDialog = ref(false)
    const isClearing = ref(false)
    
    const fetchActiveBadgeJobs = async () => {
      try {
        const response = await api.jobs.getActiveBadgeJobs()
        const data = response.data
        
        if (data.success) {
          activeBatches.value = data.active_batches || []
          totalActiveJobs.value = data.total_active_jobs || 0
        }
      } catch (error) {
        console.error('Error fetching active badge jobs:', error)
        // Set empty arrays to avoid component errors
        activeBatches.value = []
        totalActiveJobs.value = 0
      }
    }
    
    // Computed properties
    const hasCompletedBatches = computed(() => {
      return activeBatches.value.some(batch => batch.is_complete)
    })
    
    const completedBatchCount = computed(() => {
      return activeBatches.value.filter(batch => batch.is_complete).length
    })
    
    // Methods
    const showClearConfirmation = () => {
      showClearDialog.value = true
    }
    
    const clearCompletedBatches = async () => {
      isClearing.value = true
      try {
        const response = await api.jobs.clearCompletedBatches()
        const data = response.data
        
        if (data.success) {
          // Refresh the active batches immediately
          await fetchActiveBadgeJobs()
          showClearDialog.value = false
          
          // Optional: Show success message
          console.log(`✅ ${data.message}`)
        } else {
          console.error('Failed to clear batches:', data.error)
        }
      } catch (error) {
        console.error('Error clearing batches:', error)
      } finally {
        isClearing.value = false
      }
    }
    
    const startPolling = () => {
      // Poll every 3 seconds
      pollInterval.value = setInterval(fetchActiveBadgeJobs, 3000)
    }
    
    const stopPolling = () => {
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
        pollInterval.value = null
      }
    }
    
    onMounted(() => {
      fetchActiveBadgeJobs()
      startPolling()
    })
    
    onUnmounted(() => {
      stopPolling()
    })
    
    return {
      activeBatches,
      totalActiveJobs,
      hasCompletedBatches,
      completedBatchCount,
      showClearDialog,
      isClearing,
      showClearConfirmation,
      clearCompletedBatches
    }
  }
}
</script>
