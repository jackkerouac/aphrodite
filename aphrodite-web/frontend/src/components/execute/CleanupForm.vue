<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Poster Management</h2>
      <p class="text-sm opacity-70 mb-4">
        Manage your poster collection with cleanup and restore options.
      </p>
      
      <!-- Action Tabs -->
      <div class="tabs tabs-boxed mb-4">
        <a 
          class="tab" 
          :class="{ 'tab-active': actionType === 'cleanup' }"
          @click="actionType = 'cleanup'"
        >
          Clean Up Posters
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': actionType === 'restore' }"
          @click="actionType = 'restore'"
        >
          Restore Originals
        </a>
      </div>
      
      <!-- Cleanup Form -->
      <form v-if="actionType === 'cleanup'" @submit.prevent="submitCleanup">
        <div class="alert alert-warning mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <span>Warning: Cleanup operations cannot be undone!</span>
        </div>
        
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
        </div>
        
        <!-- Submit Button -->
        <div class="card-actions justify-end">
          <button 
            type="submit" 
            class="btn btn-error" 
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
      
      <!-- Restore Form -->
      <form v-else-if="actionType === 'restore'" @submit.prevent="submitRestore">
        <div class="alert alert-info mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>This will replace all modified posters with their original versions. Badge modifications will be lost.</span>
        </div>
        
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text">Restore Action</span>
          </label>
          <p class="text-sm opacity-70 mb-2">
            This operation will copy all files from the 'original' directory to the 'modified' directory, 
            effectively removing any badge modifications that have been applied to your posters.
          </p>
        </div>
        
        <!-- Submit Button -->
        <div class="card-actions justify-end">
          <button 
            type="submit" 
            class="btn btn-warning" 
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting">
              <span class="loading loading-spinner loading-sm"></span>
              Restoring...
            </span>
            <span v-else>Restore Original Posters</span>
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
    const actionType = ref('cleanup');
    
    const formData = reactive({
      cleanModified: true,
      cleanWorking: true,
      cleanOriginal: true
    });
    
    const isSubmitting = ref(false);
    
    const anyDirSelected = computed(() => {
      return formData.cleanModified || formData.cleanWorking || formData.cleanOriginal;
    });
    
    const submitCleanup = async () => {
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
    
    const submitRestore = async () => {
      isSubmitting.value = true;
      
      try {
        console.log('Submitting restore request...');
        
        // Use the shared API client to call the new restore endpoint
        const response = await api.post('/api/process/restore-originals');
        
        console.log('Restore response:', response.data);
        
        // Notify parent component of successful submission
        emit('cleanup-submitted', response.data);
        
      } catch (error) {
        console.error('Restore error:', error);
        
        let errorMessage = 'An error occurred while restoring original posters.';
        
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
      actionType,
      formData,
      isSubmitting,
      anyDirSelected,
      submitCleanup,
      submitRestore
    };
  }
}
</script>
