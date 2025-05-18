<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Clean Up Posters</h2>
      <p class="text-sm opacity-70 mb-4">
        Clean up poster directories by removing all poster files. This is useful to free up disk space after processing.
      </p>
      
      <form @submit.prevent="submitForm">
        <!-- Cleanup Options -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Directories to Clean</span>
          </label>
          
          <div class="flex flex-col gap-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                v-model="formData.cleanModified"
              />
              <span>Modified Posters</span>
            </label>
            
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                v-model="formData.cleanWorking"
              />
              <span>Working Posters</span>
            </label>
            
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                v-model="formData.cleanOriginal"
              />
              <span>Original Posters</span>
            </label>
          </div>
          
          <label class="label">
            <span class="label-text-alt">Warning: This action cannot be undone</span>
          </label>
        </div>
        
        <!-- Submit Button -->
        <div class="card-actions justify-end">
          <button 
            type="submit" 
            class="btn btn-primary" 
            :disabled="isSubmitting || !anyDirSelected"
          >
            <span v-if="isSubmitting">
              <span class="loading loading-spinner loading-sm"></span>
              Cleaning...
            </span>
            <span v-else>Clean Up Posters</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive, computed } from 'vue';
import api from '@/api';

export default {
  name: 'CleanupForm',
  emits: ['cleanup-submitted'],
  setup(props, { emit }) {
    const formData = reactive({
      cleanModified: true,
      cleanWorking: true,
      cleanOriginal: true
    });
    
    const isSubmitting = ref(false);
    
    const anyDirSelected = computed(() => {
      return formData.cleanModified || formData.cleanWorking || formData.cleanOriginal;
    });
    
    const submitForm = async () => {
      if (!anyDirSelected.value) {
        return;
      }
      
      isSubmitting.value = true;
      
      try {
        console.log('Submitting cleanup request:', {
          skipModified: !formData.cleanModified,
          skipWorking: !formData.cleanWorking,
          skipOriginal: !formData.cleanOriginal
        });
        
        // Use the shared API client
        const response = await api.post('/api/process/cleanup', {
          skipModified: !formData.cleanModified,
          skipWorking: !formData.cleanWorking,
          skipOriginal: !formData.cleanOriginal
        });
        
        console.log('Cleanup response:', response.data);
        
        // Notify parent component of successful submission
        emit('cleanup-submitted', response.data);
        
      } catch (error) {
        console.error('Cleanup error:', error);
        
        let errorMessage = 'An error occurred while cleaning up poster directories.';
        
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
        emit('cleanup-submitted', {
          success: false,
          message: errorMessage
        });
      } finally {
        isSubmitting.value = false;
      }
    };
    
    return {
      formData,
      isSubmitting,
      anyDirSelected,
      submitForm
    };
  }
}
</script>
