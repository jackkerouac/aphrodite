<template>
  <div class="workflow-manager">
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title">
          Workflow Manager
          <div class="badge badge-primary" v-if="hasActiveWorkflows">Active</div>
        </h2>
        
        <p class="text-sm opacity-70 mb-4">
          Monitor and manage batch processing workflows.
        </p>
        
        <!-- Loading state -->
        <div v-if="isLoading" class="flex justify-center my-4">
          <span class="loading loading-spinner loading-md"></span>
        </div>
        
        <!-- Active Workflows -->
        <div v-if="hasActiveWorkflows" class="mb-4">
          <h3 class="font-semibold text-lg mb-2">Active Workflows</h3>
          
          <div 
            v-for="workflow in activeWorkflows" 
            :key="workflow.id" 
            class="card bg-base-200 mb-2 p-4"
          >
            <div class="flex justify-between items-center">
              <div>
                <span class="font-medium">{{ getWorkflowTypeLabel(workflow.type) }}</span>
                <div class="badge badge-secondary badge-sm ml-2">{{ workflow.status }}</div>
              </div>
              <div class="flex items-center">
                <span class="text-xs opacity-70">Started {{ formatTime(workflow.start_time) }}</span>
              </div>
            </div>
            
            <div class="mt-2">
              <p class="text-sm">
                Processing {{ workflow.options.libraryIds?.length || 0 }} libraries 
                with {{ workflow.options.badgeTypes?.length || 0 }} badge types
              </p>
              
              <!-- Progress indicators could be added here -->
              <div class="flex justify-center my-3">
                <span class="loading loading-dots loading-md"></span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Queued Workflows -->
        <div v-if="hasQueuedWorkflows" class="mb-4">
          <h3 class="font-semibold text-lg mb-2">Queued Workflows</h3>
          
          <div 
            v-for="workflow in queuedWorkflows" 
            :key="workflow.id" 
            class="card bg-base-200 mb-2 p-4"
          >
            <div class="flex justify-between items-center">
              <div>
                <span class="font-medium">{{ getWorkflowTypeLabel(workflow.type) }}</span>
                <div class="badge badge-sm ml-2">Queue #{{ workflow.queue_position }}</div>
              </div>
              <div class="flex items-center">
                <span class="text-xs opacity-70">Created {{ formatTime(workflow.created_at) }}</span>
                <div class="ml-2">
                  <button 
                    class="btn btn-xs btn-error mr-1"
                    @click="cancelWorkflow(workflow.id)"
                    :disabled="isCancelling"
                    title="Cancel"
                  >
                    Cancel
                  </button>
                  <button 
                    class="btn btn-xs btn-ghost text-error"
                    @click="deleteWorkflow(workflow.id)"
                    :disabled="isDeleting"
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
            
            <div class="mt-2">
              <p class="text-sm">
                Will process {{ workflow.options.libraryIds?.length || 0 }} libraries 
                with {{ workflow.options.badgeTypes?.length || 0 }} badge types
              </p>
            </div>
          </div>
        </div>
        
        <!-- No Workflows -->
        <div v-if="!hasActiveWorkflows && !hasQueuedWorkflows && !isLoading" class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
          <span>No active or queued workflows. Use the form below to process libraries.</span>
        </div>
        
        <!-- Recent Completed Workflows (limited to 3) -->
        <div v-if="recentCompletedWorkflows.length > 0" class="mt-4">
          <h3 class="font-semibold text-lg mb-2">Recent Completed Workflows</h3>
          
          <div 
            v-for="workflow in recentCompletedWorkflows" 
            :key="workflow.id" 
            class="card bg-base-200 mb-2 p-4"
            :class="{
              'border-l-4 border-success': workflow.status === 'Success',
              'border-l-4 border-error': workflow.status === 'Failed',
              'border-l-4 border-warning': workflow.status === 'Cancelled'
            }"
          >
            <div class="flex justify-between items-center">
              <div>
                <span class="font-medium">{{ getWorkflowTypeLabel(workflow.type) }}</span>
                <div 
                  class="badge badge-sm ml-2"
                  :class="{
                    'badge-success': workflow.status === 'Success',
                    'badge-error': workflow.status === 'Failed',
                    'badge-warning': workflow.status === 'Cancelled'
                  }"
                >
                  {{ workflow.status }}
                </div>
              </div>
              <div class="flex items-center">
                <span class="text-xs opacity-70 mr-2">Completed {{ formatTime(workflow.end_time) }}</span>
                <button 
                  class="btn btn-xs btn-ghost text-error"
                  @click="deleteWorkflow(workflow.id)"
                  :disabled="isDeleting"
                  title="Delete"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div class="mt-2">
              <p class="text-sm">
                Processed {{ workflow.options.libraryIds?.length || 0 }} libraries 
                with {{ workflow.options.badgeTypes?.length || 0 }} badge types
              </p>
              
              <!-- Show success/failure count if available -->
              <div v-if="workflow.result && workflow.result.results" class="mt-2">
                <p class="text-xs">
                  <span class="text-success">
                    {{ workflow.result.results.filter(r => r.success).length }} successful
                  </span> / 
                  <span class="text-error">
                    {{ workflow.result.results.filter(r => !r.success).length }} failed
                  </span>
                </p>
                
                <!-- Error details -->
                <div v-if="workflow.status === 'Failed' || !workflow.result.success" class="mt-2">
                  <div class="collapse collapse-arrow bg-base-200">
                    <input type="radio" name="error-accordion" /> 
                    <div class="collapse-title text-xs font-medium">
                      View error details
                    </div>
                    <div class="collapse-content text-xs">
                      <div v-for="(result, index) in workflow.result.results" :key="index">
                        <div v-if="!result.success" class="p-2 mb-2 bg-base-300 rounded">
                          <p class="font-semibold">Library ID: {{ result.libraryId }}</p>
                          <p v-if="result.error" class="text-error">{{ result.error }}</p>
                          <p v-if="result.stderr" class="text-error mt-1">{{ result.stderr }}</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useWorkflowStore } from '@/store/workflow';

export default {
  name: 'WorkflowManager',
  setup() {
    const workflowStore = useWorkflowStore();
    const isCancelling = ref(false);
    const isDeleting = ref(false);
    
    // Computed properties
    const isLoading = computed(() => workflowStore.isLoading);
    const activeWorkflows = computed(() => workflowStore.activeWorkflows);
    const queuedWorkflows = computed(() => workflowStore.queuedWorkflows);
    const completedWorkflows = computed(() => workflowStore.completedWorkflows);
    const recentCompletedWorkflows = computed(() => 
      completedWorkflows.value.slice(0, 3)
    );
    
    const hasActiveWorkflows = computed(() => activeWorkflows.value.length > 0);
    const hasQueuedWorkflows = computed(() => queuedWorkflows.value.length > 0);
    
    // Methods
    const getWorkflowTypeLabel = (type) => {
      const types = {
        'library_batch': 'Library Batch Processing',
        'item_batch': 'Item Batch Processing'
      };
      
      return types[type] || type;
    };
    
    const formatTime = (isoString) => {
      if (!isoString) return 'Unknown';
      
      try {
        const date = new Date(isoString);
        return date.toLocaleString();
      } catch (e) {
        return isoString;
      }
    };
    
    const cancelWorkflow = async (workflowId) => {
      isCancelling.value = true;
      
      try {
        const result = await workflowStore.cancelWorkflow(workflowId);
        
        if (!result.success) {
          alert(result.message || 'Failed to cancel workflow');
        }
      } catch (error) {
        console.error('Error cancelling workflow:', error);
        alert('An error occurred while cancelling the workflow');
      } finally {
        isCancelling.value = false;
      }
    };
    
    const deleteWorkflow = async (workflowId) => {
      // Ask for confirmation before deleting
      if (!confirm('Are you sure you want to delete this workflow? This action cannot be undone.')) {
        return;
      }
      
      isDeleting.value = true;
      
      try {
        const result = await workflowStore.deleteWorkflow(workflowId);
        
        if (!result.success) {
          alert(result.message || 'Failed to delete workflow');
        }
      } catch (error) {
        console.error('Error deleting workflow:', error);
        alert('An error occurred while deleting the workflow');
      } finally {
        isDeleting.value = false;
      }
    };
    
    // Lifecycle hooks
    onMounted(() => {
      // Fetch workflows and start polling
      workflowStore.fetchWorkflows();
      workflowStore.startPolling();
    });
    
    onUnmounted(() => {
      // Stop polling when component is unmounted
      workflowStore.stopPolling();
    });
    
    return {
      isLoading,
      activeWorkflows,
      queuedWorkflows,
      completedWorkflows,
      recentCompletedWorkflows,
      hasActiveWorkflows,
      hasQueuedWorkflows,
      isCancelling,
      isDeleting,
      getWorkflowTypeLabel,
      formatTime,
      cancelWorkflow,
      deleteWorkflow
    };
  }
}
</script>
