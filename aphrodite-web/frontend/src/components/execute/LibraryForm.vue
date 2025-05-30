<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Process Library</h2>
      <p class="text-sm opacity-70 mb-4">
        Select libraries to process and configure options.
      </p>
      
      <form @submit.prevent="submitForm">
        <!-- Loading State -->
        <div v-if="isLoadingLibraries" class="flex justify-center py-8">
          <span class="loading loading-spinner loading-md"></span>
          <span class="ml-2">Loading libraries...</span>
        </div>
        
        <!-- Libraries Selection -->
        <div v-else class="form-control mb-4">
          <label class="label">
            <span class="label-text">Jellyfin Libraries</span>
            <span class="label-text-alt">Select at least one</span>
          </label>
          
          <div v-if="libraries.length === 0" class="alert alert-warning">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <span>No libraries found. Please check your Jellyfin connection.</span>
          </div>
          
          <div v-else class="flex flex-col gap-2 mt-2 max-h-48 overflow-y-auto p-2 border rounded-lg">
            <label v-for="library in libraries" :key="library.id" class="flex items-center gap-2 cursor-pointer p-2 hover:bg-base-200 rounded-md">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                :value="library.id"
                v-model="formData.libraryIds"
              />
              <div>
                <span class="font-medium">{{ library.name }}</span>
                <span class="text-xs opacity-70 ml-2">({{ library.itemCount }} items)</span>
              </div>
            </label>
          </div>
          
          <label class="label" v-if="errors.libraries">
            <span class="label-text-alt text-error">{{ errors.libraries }}</span>
          </label>
        </div>
        
        <!-- Item Limit -->
        <div class="form-control w-full mb-4">
          <label class="label">
            <span class="label-text">Item Limit</span>
            <span class="label-text-alt">Leave empty for all items</span>
          </label>
          <input 
            type="number"
            placeholder="Optional limit on number of items to process"
            class="input input-bordered w-full"
            min="1"
            v-model.number="formData.limit"
          />
          <label class="label">
            <span class="label-text-alt">Processing many items can take a long time</span>
          </label>
        </div>
        
        <!-- Retries -->
        <div class="form-control w-full mb-4">
          <label class="label">
            <span class="label-text">Maximum Retries</span>
          </label>
          <input 
            type="number"
            class="input input-bordered w-full"
            min="1"
            max="10"
            v-model.number="formData.retries"
          />
          <label class="label">
            <span class="label-text-alt">Number of times to retry failed operations</span>
          </label>
        </div>
        
        <!-- Badge Type Selection -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Badge Types</span>
            <span class="label-text-alt">Select at least one</span>
          </label>
          
          <div class="flex flex-col gap-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                v-model="formData.badges.audio"
              />
              <span>Audio Badge</span>
            </label>
            
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                v-model="formData.badges.resolution"
              />
              <span>Resolution Badge</span>
            </label>
            
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                v-model="formData.badges.review"
              />
              <span>Review Badge</span>
            </label>
          </div>
          
          <label class="label" v-if="errors.badges">
            <span class="label-text-alt text-error">{{ errors.badges }}</span>
          </label>
        </div>
        
        <!-- Processing Options -->
        <div class="form-control mb-6">
          <label class="flex items-center gap-2 cursor-pointer mb-2">
            <input 
              type="checkbox" 
              class="checkbox checkbox-primary" 
              v-model="formData.skipUpload"
            />
            <span>Skip upload to Jellyfin</span>
          </label>
          
          <label class="flex items-center gap-2 cursor-pointer">
            <input 
              type="checkbox" 
              class="checkbox checkbox-primary" 
              v-model="formData.skipProcessed"
            />
            <span>Skip items already processed by Aphrodite</span>
          </label>
          <label class="label">
            <span class="label-text-alt">Items with the aphrodite-overlay tag will be skipped</span>
          </label>
        </div>
        
        <!-- Submit Button -->
        <div class="card-actions justify-end">
          <button 
            type="submit" 
            class="btn btn-primary" 
            :disabled="isSubmitting || isLoadingLibraries || libraries.length === 0"
          >
            <span v-if="isSubmitting">
              <span class="loading loading-spinner loading-sm"></span>
              Processing...
            </span>
            <span v-else>Process Libraries</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import api from '@/api';
import { useWorkflowStore } from '@/store/workflow';

export default {
  name: 'LibraryForm',
  emits: ['process-submitted'],
  setup(props, { emit }) {
    const libraries = ref([]);
    const isLoadingLibraries = ref(true);
    const isSubmitting = ref(false);
    const workflowStore = useWorkflowStore();
    
    const formData = reactive({
      libraryIds: [],
      limit: null,
      retries: 3,
      badges: {
        audio: true,
        resolution: true,
        review: true
      },
      skipUpload: false,
      skipProcessed: false
    });
    
    const errors = reactive({
      libraries: '',
      badges: ''
    });
    
    // Fetch libraries from Jellyfin
    const fetchLibraries = async () => {
      isLoadingLibraries.value = true;
      
      try {
        // Call the API to get libraries
        const response = await api.get('/api/libraries/');
        
        if (response.data.success && response.data.libraries) {
          libraries.value = response.data.libraries;
        } else {
          libraries.value = [];
          console.error('Error fetching libraries:', response.data.message);
        }
      } catch (error) {
        console.error('Error fetching libraries:', error);
        libraries.value = [];
      } finally {
        isLoadingLibraries.value = false;
      }
    };
    
    const validateForm = () => {
      let valid = true;
      
      // Clear previous errors
      errors.libraries = '';
      errors.badges = '';
      
      // Validate library selection
      if (!formData.libraryIds.length) {
        errors.libraries = 'At least one library must be selected';
        valid = false;
      }
      
      // Validate at least one badge is selected
      if (!formData.badges.audio && !formData.badges.resolution && !formData.badges.review) {
        errors.badges = 'At least one badge type must be selected';
        valid = false;
      }
      
      return valid;
    };
    
    const submitForm = async () => {
      if (!validateForm()) {
        return;
      }
      
      isSubmitting.value = true;
      
      try {
        // Prepare badge types array
        const badgeTypes = [];
        if (formData.badges.audio) badgeTypes.push('audio');
        if (formData.badges.resolution) badgeTypes.push('resolution');
        if (formData.badges.review) badgeTypes.push('review');
        
        console.log('Creating workflow for library batch processing:', {
          libraryIds: formData.libraryIds,
          limit: formData.limit,
          retries: formData.retries,
          badgeTypes,
          skipUpload: formData.skipUpload
        });
        
        // Use workflow store to create a library batch workflow
        const response = await workflowStore.createLibraryBatchWorkflow({
          libraryIds: formData.libraryIds,
          limit: formData.limit,
          retries: formData.retries,
          badgeTypes,
          skipUpload: formData.skipUpload,
          skipProcessed: formData.skipProcessed
        });
        
        console.log('Workflow creation response:', response);
        
        // Notify parent component of successful submission
        emit('process-submitted', {
          success: response.success,
          message: response.message || (response.success ? 'Workflow added to queue' : 'Failed to create workflow'),
          workflowId: response.workflowId
        });
        
      } catch (error) {
        console.error('Workflow creation error:', error);
        
        let errorMessage = 'An error occurred while creating the workflow.';
        
        if (error.response) {
          console.error('Error response:', error.response.data);
          errorMessage = error.response.data.message || 
                       `Server error: ${error.response.status}`;
        } else if (error.request) {
          console.error('Error request:', error.request);
          errorMessage = 'No response from server. Please check if the server is running.';
        } else {
          console.error('Error message:', error.message);
          errorMessage = error.message;
        }
        
        // Notify parent of the error
        emit('process-submitted', {
          success: false,
          message: errorMessage
        });
      } finally {
        isSubmitting.value = false;
      }
    };
    
    // Fetch libraries when component is mounted
    onMounted(() => {
      fetchLibraries();
    });
    
    return {
      libraries,
      isLoadingLibraries,
      isSubmitting,
      formData,
      errors,
      submitForm
    };
  }
}
</script>
