<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Process Single Item</h2>
      <p class="text-sm opacity-70 mb-4">
        Enter a Jellyfin item ID and select which badges to apply.
      </p>
      
      <form @submit.prevent="submitForm">
        <!-- Item ID Input -->
        <div class="form-control w-full mb-4">
          <label class="label">
            <span class="label-text">Jellyfin Item ID</span>
            <span class="label-text-alt">Required</span>
          </label>
          <input 
            type="text"
            placeholder="Enter Jellyfin item ID"
            class="input input-bordered w-full"
            v-model="formData.itemId"
            required
          />
          <label class="label" v-if="errors.itemId">
            <span class="label-text-alt text-error">{{ errors.itemId }}</span>
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
            
            <label class="flex items-center gap-2 cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-primary" 
                v-model="formData.badges.awards"
              />
              <span>Awards Badge</span>
            </label>
          </div>
          
          <label class="label" v-if="errors.badges">
            <span class="label-text-alt text-error">{{ errors.badges }}</span>
          </label>
        </div>
        
        <!-- Upload Option -->
        <div class="form-control mb-6">
          <label class="flex items-center gap-2 cursor-pointer">
            <input 
              type="checkbox" 
              class="checkbox checkbox-primary" 
              v-model="formData.skipUpload"
            />
            <span>Skip upload to Jellyfin</span>
          </label>
        </div>
        
        <!-- Submit Button -->
        <div class="card-actions justify-end">
          <button 
            type="submit" 
            class="btn btn-primary" 
            :disabled="isSubmitting"
          >
            <span v-if="isSubmitting">
              <span class="loading loading-spinner loading-sm"></span>
              Processing...
            </span>
            <span v-else>Process Item</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, reactive } from 'vue';
import api from '@/api';

export default {
  name: 'ItemForm',
  emits: ['process-submitted'],
  setup(props, { emit }) {
    const formData = reactive({
      itemId: '',
      badges: {
        audio: true,
        resolution: false,
        review: false,
        awards: false
      },
      skipUpload: false
    });
    
    const errors = reactive({
      itemId: '',
      badges: ''
    });
    
    const isSubmitting = ref(false);
    
    const validateForm = () => {
      let valid = true;
      
      // Clear previous errors
      errors.itemId = '';
      errors.badges = '';
      
      // Validate Item ID
      if (!formData.itemId.trim()) {
        errors.itemId = 'Item ID is required';
        valid = false;
      }
      
      // Validate at least one badge is selected
      if (!formData.badges.audio && !formData.badges.resolution && !formData.badges.review && !formData.badges.awards) {
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
        if (formData.badges.awards) badgeTypes.push('awards');
        
        console.log('Submitting process request:', {
          itemId: formData.itemId,
          badgeTypes,
          skipUpload: formData.skipUpload
        });
        
        // Use the shared API client
        const response = await api.post('/api/process/item', {
          itemId: formData.itemId,
          badgeTypes,
          skipUpload: formData.skipUpload
        });
        
        console.log('Process response:', response.data);
        
        // Notify parent component of successful submission
        emit('process-submitted', response.data);
        
      } catch (error) {
        console.error('Processing error:', error);
        
        let errorMessage = 'An error occurred while processing the request.';
        
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
    
    return {
      formData,
      errors,
      isSubmitting,
      submitForm
    };
  }
}
</script>
