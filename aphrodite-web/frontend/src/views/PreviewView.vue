<template>
  <div class="preview">
    <h1 class="text-2xl font-bold mb-6">Preview</h1>
    
    <!-- Two cards side by side -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Settings card on the left -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Settings</h2>
          <p class="text-base-content opacity-70 mb-4">Configure your preview settings here. Aphrodite will use a random poster from your Jellyfin library.</p>
          
          <!-- Badge Types Selection -->
          <div class="form-control mb-6">
            <label class="label">
              <span class="label-text font-semibold">Badge Types</span>
            </label>
            <div class="space-y-2">
              <div v-for="badgeType in availableBadgeTypes" :key="badgeType.id" class="form-control">
                <label class="label cursor-pointer">
                  <div class="flex-1">
                    <span class="label-text">{{ badgeType.name }}</span>
                    <div class="text-xs text-base-content opacity-60">{{ badgeType.description }}</div>
                  </div>
                  <input 
                    type="checkbox" 
                    :value="badgeType.id"
                    v-model="selectedBadgeTypes"
                    class="checkbox checkbox-primary" 
                  />
                </label>
              </div>
            </div>
          </div>
          
          <!-- Generate Button -->
          <button 
            class="btn btn-primary btn-block"
            :class="{ 'loading': isGenerating }"
            :disabled="isGenerating || selectedBadgeTypes.length === 0"
            @click="generatePreview"
          >
            {{ isGenerating ? 'Generating...' : 'Generate Preview' }}
          </button>
          
          <!-- Error message -->
          <div v-if="error" class="alert alert-error mt-4">
            <div>
              <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>{{ error }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Preview Poster card on the right -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Preview Poster</h2>
          
          <!-- Loading state -->
          <div v-if="isGenerating" class="flex flex-col items-center justify-center py-12">
            <div class="loading loading-spinner loading-lg mb-4"></div>
            <p class="text-base-content opacity-70">Generating preview...</p>
          </div>
          
          <!-- Preview image -->
          <div v-else-if="previewImageUrl" class="flex flex-col items-center">
            <img 
              :src="previewImageUrl" 
              alt="Preview Poster"
              class="max-w-full h-auto rounded-lg shadow-md mb-4"
              style="max-height: 500px;"
            />
            <p class="text-sm text-base-content opacity-70 text-center">
              Preview generated with {{ selectedBadgeTypes.join(', ') }} badges
              <span v-if="sourcePosterName">using "{{ sourcePosterName }}"</span>
            </p>
          </div>
          
          <!-- Placeholder state -->
          <div v-else class="flex flex-col items-center justify-center py-12">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 text-base-content opacity-30 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            <p class="text-base-content opacity-70">Your poster preview will appear here.</p>
            <p class="text-sm text-base-content opacity-50 mt-2">Select badge types and click "Generate Preview"</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import api from '@/api';

export default {
  name: 'PreviewView',
  setup() {
    const selectedBadgeTypes = ref(['audio', 'resolution']);
    const availableBadgeTypes = ref([]);
    const isGenerating = ref(false);
    const error = ref(null);
    const previewImageUrl = ref(null);
    const sourcePosterName = ref(null);
    const currentJobId = ref(null);
    
    // Load available options on mount
    onMounted(async () => {
      console.log('PreviewView mounted, loading data...');
      console.log('API object:', api);
      console.log('Preview API:', api.preview);
      
      if (!api.preview) {
        error.value = 'Preview API not available';
        return;
      }
      
      await loadBadgeTypes();
    });
    
    // Load available badge types
    const loadBadgeTypes = async () => {
      try {
        console.log('Loading badge types...');
        const response = await api.preview.getBadgeTypes();
        console.log('Badge types response:', response);
        console.log('Response data:', response.data);
        console.log('Response success:', response.data.success);
        console.log('Badge types array:', response.data.badgeTypes);
        
        if (response.data.success && response.data.badgeTypes) {
          availableBadgeTypes.value = response.data.badgeTypes;
          console.log('Badge types loaded successfully:', availableBadgeTypes.value);
        } else {
          throw new Error('Invalid response format or success=false');
        }
      } catch (err) {
        console.error('Error loading badge types:', err);
        console.error('Full error details:', err.response || err.message);
        error.value = `Failed to load badge types: ${err.response?.data?.message || err.message}`;
      }
    };
    
    // Generate preview
    const generatePreview = async () => {
      if (selectedBadgeTypes.value.length === 0) {
        error.value = 'Please select at least one badge type';
        return;
      }
      
      isGenerating.value = true;
      error.value = null;
      previewImageUrl.value = null;
      sourcePosterName.value = null;
      
      try {
        const response = await api.preview.generatePreview({
          badgeTypes: selectedBadgeTypes.value
        });
        
        if (response.data.success) {
          currentJobId.value = response.data.jobId;
          // Poll for job completion
          pollJobStatus();
        } else {
          error.value = response.data.message || 'Failed to start preview generation';
          isGenerating.value = false;
        }
      } catch (err) {
        console.error('Error generating preview:', err);
        error.value = 'Failed to generate preview. Please try again.';
        isGenerating.value = false;
      }
    };
    
    // Poll job status until completion
    const pollJobStatus = async () => {
      if (!currentJobId.value) return;
      
      try {
        const response = await api.jobs.getJob(currentJobId.value);
        const job = response.data.job;
        
        if (job.status === 'success') {
          // Job completed successfully
          if (job.result && job.result.poster_url) {
            previewImageUrl.value = job.result.poster_url;
            sourcePosterName.value = job.result.source_poster || 'Unknown';
          } else {
            error.value = 'Preview generated but image not found';
          }
          isGenerating.value = false;
        } else if (job.status === 'failed') {
          // Job failed
          error.value = job.result?.error || 'Preview generation failed';
          isGenerating.value = false;
        } else {
          // Job still running, poll again
          setTimeout(pollJobStatus, 2000);
        }
      } catch (err) {
        console.error('Error polling job status:', err);
        error.value = 'Failed to check preview status';
        isGenerating.value = false;
      }
    };
    
    return {
      selectedBadgeTypes,
      availableBadgeTypes,
      isGenerating,
      error,
      previewImageUrl,
      sourcePosterName,
      generatePreview
    };
  }
};
</script>
