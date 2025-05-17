import { defineStore } from 'pinia';
import axios from 'axios';

export const useWorkflowStore = defineStore('workflow', {
  state: () => ({
    activeWorkflows: [],
    queuedWorkflows: [],
    completedWorkflows: [],
    isLoading: false,
    error: null,
    pollInterval: null
  }),
  
  getters: {
    hasActiveWorkflows: (state) => state.activeWorkflows.length > 0,
    hasQueuedWorkflows: (state) => state.queuedWorkflows.length > 0,
    totalWorkflows: (state) => 
      state.activeWorkflows.length + 
      state.queuedWorkflows.length
  },
  
  actions: {
    async fetchWorkflows() {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.get('http://localhost:5000/api/workflow/');
        
        if (response.data.success) {
          this.activeWorkflows = response.data.active;
          this.queuedWorkflows = response.data.queue;
          this.completedWorkflows = response.data.completed;
        } else {
          this.error = response.data.message || 'Failed to fetch workflows';
        }
      } catch (error) {
        console.error('Error fetching workflows:', error);
        this.error = error.message || 'Failed to fetch workflows';
      } finally {
        this.isLoading = false;
      }
    },
    
    async createLibraryBatchWorkflow(options) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.post('http://localhost:5000/api/workflow/library-batch', options);
        
        if (response.data.success) {
          await this.fetchWorkflows();
          return response.data;
        } else {
          this.error = response.data.message || 'Failed to create workflow';
          return { success: false, message: this.error };
        }
      } catch (error) {
        console.error('Error creating workflow:', error);
        this.error = error.message || 'Failed to create workflow';
        return { success: false, message: this.error };
      } finally {
        this.isLoading = false;
      }
    },
    
    async cancelWorkflow(workflowId) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.post(`http://localhost:5000/api/workflow/${workflowId}/cancel`);
        
        if (response.data.success) {
          await this.fetchWorkflows();
          return response.data;
        } else {
          this.error = response.data.message || 'Failed to cancel workflow';
          return { success: false, message: this.error };
        }
      } catch (error) {
        console.error('Error cancelling workflow:', error);
        this.error = error.message || 'Failed to cancel workflow';
        return { success: false, message: this.error };
      } finally {
        this.isLoading = false;
      }
    },
    
    async deleteWorkflow(workflowId) {
      this.isLoading = true;
      this.error = null;
      
      try {
        const response = await axios.delete(`http://localhost:5000/api/workflow/${workflowId}`);
        
        if (response.data.success) {
          await this.fetchWorkflows();
          return response.data;
        } else {
          this.error = response.data.message || 'Failed to delete workflow';
          return { success: false, message: this.error };
        }
      } catch (error) {
        console.error('Error deleting workflow:', error);
        this.error = error.message || 'Failed to delete workflow';
        return { success: false, message: this.error };
      } finally {
        this.isLoading = false;
      }
    },
    
    startPolling() {
      // Stop any existing polling
      this.stopPolling();
      
      // Start polling every 5 seconds
      this.pollInterval = setInterval(() => {
        this.fetchWorkflows();
      }, 5000);
    },
    
    stopPolling() {
      if (this.pollInterval) {
        clearInterval(this.pollInterval);
        this.pollInterval = null;
      }
    }
  }
});
