<template>
  <div v-if="activeBatches.length > 0 || activeWorkflows.length > 0" class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        Active Processing
      </h2>
      
      <div class="space-y-3">
        <!-- Active Poster Badge Batches -->
        <div v-for="batch in activeBatches" :key="batch.batch_id" class="border border-base-300 rounded-lg p-3">
          <div class="flex justify-between items-start mb-2">
            <div>
              <div class="font-medium text-sm">
                <span class="badge badge-primary badge-sm mr-2">Poster Badges</span>
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
        
        <!-- Active Scheduled Workflows -->
        <div v-for="workflow in activeWorkflows" :key="workflow.workflow_id" class="border border-base-300 rounded-lg p-3">
          <div class="flex justify-between items-start mb-2">
            <div>
              <div class="font-medium text-sm">
                <span class="badge badge-accent badge-sm mr-2">Scheduled Job</span>
                {{ workflow.name }}
              </div>
              <div class="text-xs opacity-60">
                <span v-if="workflow.badge_types.length > 0">Badges: {{ workflow.badge_types.join(', ') }}</span>
                <span v-else>Library processing</span>
              </div>
            </div>
            <div class="text-right">
              <div class="text-sm">
                <span class="badge" :class="getStatusBadgeClass(workflow.status)">
                  {{ workflow.status }}
                </span>
              </div>
              <div v-if="workflow.queue_position" class="text-xs opacity-60">
                Position: {{ workflow.queue_position }}
              </div>
            </div>
          </div>
          
          <!-- Progress Bar (indeterminate for workflows) -->
          <progress v-if="workflow.status === 'Running'" class="progress progress-accent w-full h-2 mb-2"></progress>
          <div v-else-if="workflow.status === 'Queued'" class="bg-base-200 w-full h-2 mb-2 rounded"></div>
          
          <!-- Action Button -->
          <button 
            class="btn btn-xs btn-outline btn-accent w-full"
            @click="viewWorkflowDetails(workflow.workflow_id)"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            View Details
          </button>
        </div>
      </div>
      
      <!-- Summary -->
      <div class="flex justify-between items-center mt-3">
        <div class="stats stats-horizontal shadow bg-base-200 flex-1">
          <div class="stat py-2">
            <div class="stat-title text-xs">Badge Batches</div>
            <div class="stat-value text-sm">{{ activeBatches.length }}</div>
          </div>
          <div class="stat py-2">
            <div class="stat-title text-xs">Scheduled Jobs</div>
            <div class="stat-value text-sm text-accent">{{ activeWorkflows.length }}</div>
          </div>
          <div class="stat py-2">
            <div class="stat-title text-xs">Total Active</div>
            <div class="stat-value text-sm text-warning">{{ totalActiveJobs + totalActiveWorkflows }}</div>
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
  
  <!-- Workflow Details Modal -->
  <div v-if="showWorkflowModal" class="modal modal-open">
    <div class="modal-box max-w-2xl">
      <h3 class="font-bold text-lg mb-4">Scheduled Job Details</h3>
      
      <div v-if="selectedWorkflowDetails" class="space-y-4">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <div class="text-sm font-medium opacity-70">Workflow ID</div>
            <div class="font-mono text-xs">{{ selectedWorkflowDetails.id }}</div>
          </div>
          <div>
            <div class="text-sm font-medium opacity-70">Status</div>
            <div>
              <span class="badge" :class="getStatusBadgeClass(selectedWorkflowDetails.status)">
                {{ selectedWorkflowDetails.status }}
              </span>
            </div>
          </div>
          <div>
            <div class="text-sm font-medium opacity-70">Type</div>
            <div>{{ selectedWorkflowDetails.type }}</div>
          </div>
          <div>
            <div class="text-sm font-medium opacity-70">Created</div>
            <div class="text-sm">{{ formatDateTime(selectedWorkflowDetails.created_at) }}</div>
          </div>
        </div>
        
        <div v-if="selectedWorkflowDetails.options">
          <div class="text-sm font-medium opacity-70 mb-2">Processing Options</div>
          <div class="bg-base-200 p-3 rounded">
            <div v-if="selectedWorkflowDetails.options.libraryIds" class="mb-2">
              <span class="text-xs font-medium">Libraries:</span>
              <div class="flex flex-wrap gap-1 mt-1">
                <span v-for="libId in selectedWorkflowDetails.options.libraryIds" :key="libId" class="badge badge-sm">
                  {{ libId }}
                </span>
              </div>
            </div>
            <div v-if="selectedWorkflowDetails.options.badgeTypes" class="mb-2">
              <span class="text-xs font-medium">Badge Types:</span>
              <div class="flex flex-wrap gap-1 mt-1">
                <span v-for="badge in selectedWorkflowDetails.options.badgeTypes" :key="badge" class="badge badge-primary badge-sm">
                  {{ badge }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-if="selectedWorkflowDetails.result" class="space-y-2">
          <div class="text-sm font-medium opacity-70">Results</div>
          <div class="bg-base-200 p-3 rounded max-h-60 overflow-y-auto">
            <pre class="text-xs">{{ JSON.stringify(selectedWorkflowDetails.result, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <div v-else class="text-center py-8">
        <span class="loading loading-spinner loading-lg"></span>
        <p class="mt-4">Loading workflow details...</p>
      </div>
      
      <div class="modal-action">
        <button class="btn" @click="closeWorkflowModal">Close</button>
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
    const activeWorkflows = ref([])
    const totalActiveJobs = ref(0)
    const totalActiveWorkflows = ref(0)
    const pollInterval = ref(null)
    const showClearDialog = ref(false)
    const isClearing = ref(false)
    const showWorkflowModal = ref(false)
    const selectedWorkflowDetails = ref(null)
    
    const fetchActiveJobsWithWorkflows = async () => {
      try {
        const response = await api.jobsExtended.getActiveJobsWithWorkflows()
        const data = response.data
        
        if (data.success) {
          activeBatches.value = data.active_batches || []
          activeWorkflows.value = data.active_workflows || []
          totalActiveJobs.value = data.total_active_jobs || 0
          totalActiveWorkflows.value = data.total_active_workflows || 0
        }
      } catch (error) {
        console.error('Error fetching active jobs with workflows:', error)
        // Set empty arrays to avoid component errors
        activeBatches.value = []
        activeWorkflows.value = []
        totalActiveJobs.value = 0
        totalActiveWorkflows.value = 0
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
    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    const getStatusBadgeClass = (status) => {
      switch (status) {
        case 'Running':
          return 'badge-warning'
        case 'Queued':
          return 'badge-info'
        case 'Success':
        case 'Completed':
          return 'badge-success'
        case 'Failed':
          return 'badge-error'
        default:
          return 'badge-ghost'
      }
    }
    
    const viewWorkflowDetails = async (workflowId) => {
      try {
        selectedWorkflowDetails.value = null
        showWorkflowModal.value = true
        
        const response = await api.jobsExtended.getWorkflowDetails(workflowId)
        const data = response.data
        
        if (data.success) {
          selectedWorkflowDetails.value = data.workflow
        } else {
          console.error('Failed to load workflow details:', data.message)
        }
      } catch (error) {
        console.error('Error loading workflow details:', error)
      }
    }
    
    const closeWorkflowModal = () => {
      showWorkflowModal.value = false
      selectedWorkflowDetails.value = null
    }
    
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
          await fetchActiveJobsWithWorkflows()
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
      pollInterval.value = setInterval(fetchActiveJobsWithWorkflows, 3000)
    }
    
    const stopPolling = () => {
      if (pollInterval.value) {
        clearInterval(pollInterval.value)
        pollInterval.value = null
      }
    }
    
    onMounted(() => {
      fetchActiveJobsWithWorkflows()
      startPolling()
    })
    
    onUnmounted(() => {
      stopPolling()
    })
    
    return {
      activeBatches,
      activeWorkflows,
      totalActiveJobs,
      totalActiveWorkflows,
      hasCompletedBatches,
      completedBatchCount,
      showClearDialog,
      isClearing,
      showWorkflowModal,
      selectedWorkflowDetails,
      formatDateTime,
      getStatusBadgeClass,
      viewWorkflowDetails,
      closeWorkflowModal,
      showClearConfirmation,
      clearCompletedBatches
    }
  }
}
</script>
