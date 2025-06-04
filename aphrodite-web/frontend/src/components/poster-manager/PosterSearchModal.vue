<template>
  <div class="modal modal-open">
    <div class="modal-box w-11/12 max-w-6xl max-h-[90vh] overflow-hidden flex flex-col">
      <!-- Modal Header -->
      <div class="flex justify-between items-center mb-4 flex-shrink-0">
        <h3 class="font-bold text-lg">Search External Posters</h3>
        <button class="btn btn-sm btn-circle btn-ghost" @click="$emit('close')">✕</button>
      </div>

      <!-- Search Info -->
      <div class="mb-4 flex-shrink-0">
        <div class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Searching for alternative posters for <strong>{{ item.name }}</strong></span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <div class="text-center">
          <span class="loading loading-spinner loading-lg"></span>
          <p class="mt-2">Searching external sources...</p>
        </div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="alert alert-error mb-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>

      <!-- Filter Controls -->
      <div v-else-if="posterSources.length > 0" class="mb-4 flex-shrink-0">
        <div class="flex flex-wrap gap-2">
          <div class="form-control">
            <label class="label cursor-pointer">
              <span class="label-text mr-2">Source:</span>
              <select v-model="selectedSource" class="select select-sm select-bordered">
                <option value="">All Sources</option>
                <option v-for="source in availableSources" :key="source" :value="source">
                  {{ source }}
                </option>
              </select>
            </label>
          </div>
          
          <div class="form-control">
            <label class="label cursor-pointer">
              <span class="label-text mr-2">Sort by:</span>
              <select v-model="sortBy" class="select select-sm select-bordered">
                <option value="quality">Quality</option>
                <option value="resolution">Resolution</option>
                <option value="votes">Community Rating</option>
              </select>
            </label>
          </div>
          
          <div class="form-control">
            <label class="label cursor-pointer">
              <span class="label-text mr-2">Language:</span>
              <select v-model="selectedLanguage" class="select select-sm select-bordered">
                <option value="">All Languages</option>
                <option v-for="lang in availableLanguages" :key="lang" :value="lang">
                  {{ lang }}
                </option>
              </select>
            </label>
          </div>
        </div>
      </div>

      <!-- Poster Grid -->
      <div v-if="!isLoading && !error" class="flex-1 overflow-y-auto">
        <div v-if="filteredPosters.length === 0 && posterSources.length > 0" class="text-center py-8">
          <p class="text-gray-500">No posters match the selected filters.</p>
        </div>
        
        <div v-else-if="posterSources.length === 0" class="text-center py-8">
          <p class="text-gray-500">No external posters found for this item.</p>
        </div>
        
        <div v-else class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <div 
            v-for="poster in filteredPosters" 
            :key="poster.id"
            class="card card-compact bg-base-100 shadow-md hover:shadow-lg transition-shadow cursor-pointer"
            :class="{ 'ring-2 ring-primary': selectedPoster?.id === poster.id }"
            @click="selectPoster(poster)"
          >
            <figure class="relative">
              <img 
                :src="poster.preview_url" 
                :alt="`${poster.source} poster`"
                class="w-full h-48 object-cover"
                @error="handleImageError"
                loading="lazy"
              />
              
              <!-- Source Badge -->
              <div class="absolute top-2 left-2">
                <div class="badge badge-primary badge-sm">{{ poster.source }}</div>
              </div>
              
              <!-- Quality Badge -->
              <div class="absolute top-2 right-2">
                <div class="badge badge-secondary badge-sm">
                  {{ poster.width }}×{{ poster.height }}
                </div>
              </div>
              
              <!-- Selection Indicator -->
              <div v-if="selectedPoster?.id === poster.id" class="absolute inset-0 bg-primary bg-opacity-20 flex items-center justify-center">
                <div class="bg-primary text-primary-content rounded-full p-2">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            </figure>
            
            <div class="card-body">
              <div class="text-xs space-y-1">
                <div><strong>Language:</strong> {{ poster.language }}</div>
                <div><strong>Size:</strong> {{ poster.file_size_estimate }}</div>
                <div v-if="poster.vote_count > 0">
                  <strong>Rating:</strong> {{ poster.vote_average.toFixed(1) }}/10 ({{ poster.vote_count }} votes)
                </div>
                <div><strong>Aspect:</strong> {{ poster.aspect_ratio }}:1</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer Actions -->
      <div class="modal-action flex-shrink-0 mt-4">
        <div class="flex-1">
          <div v-if="selectedPoster" class="text-sm text-gray-600">
            Selected: {{ selectedPoster.source }} poster ({{ selectedPoster.width }}×{{ selectedPoster.height }})
          </div>
        </div>
        
        <button class="btn" @click="$emit('close')">Cancel</button>
        <button 
          class="btn btn-primary" 
          :disabled="!selectedPoster || isProcessing"
          @click="confirmSelection"
        >
          {{ isProcessing ? 'Processing...' : 'Use Selected Poster' }}
        </button>
      </div>
    </div>
  </div>

  <!-- Confirmation Dialog -->
  <ConfirmationDialog
    v-if="showConfirmDialog"
    title="Replace Poster"
    :message="confirmMessage"
    confirm-text="Replace Poster"
    type="warning"
    :is-processing="isProcessing"
    @confirm="replaceWithSelectedPoster"
    @cancel="showConfirmDialog = false"
  />
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import ConfirmationDialog from './ConfirmationDialog.vue';

export default {
  name: 'PosterSearchModal',
  components: {
    ConfirmationDialog
  },
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'poster-replaced'],
  setup(props, { emit }) {
    const isLoading = ref(true);
    const isProcessing = ref(false);
    const error = ref(null);
    const posterSources = ref([]);
    const selectedPoster = ref(null);
    const showConfirmDialog = ref(false);
    
    // Filter states
    const selectedSource = ref('');
    const selectedLanguage = ref('');
    const sortBy = ref('quality');
    
    // Computed properties
    const availableSources = computed(() => {
      const sources = [...new Set(posterSources.value.map(p => p.source))];
      return sources.sort();
    });
    
    const availableLanguages = computed(() => {
      const languages = [...new Set(posterSources.value.map(p => p.language))];
      return languages.sort();
    });
    
    const filteredPosters = computed(() => {
      let filtered = posterSources.value;
      
      if (selectedSource.value) {
        filtered = filtered.filter(p => p.source === selectedSource.value);
      }
      
      if (selectedLanguage.value) {
        filtered = filtered.filter(p => p.language === selectedLanguage.value);
      }
      
      // Sort by selected criteria
      filtered.sort((a, b) => {
        switch (sortBy.value) {
          case 'quality':
            return b.quality_score - a.quality_score;
          case 'resolution':
            return (b.width * b.height) - (a.width * a.height);
          case 'votes':
            return (b.vote_count || 0) - (a.vote_count || 0);
          default:
            return 0;
        }
      });
      
      return filtered;
    });
    
    const confirmMessage = computed(() => {
      if (!selectedPoster.value) return '';
      
      const poster = selectedPoster.value;
      return `Replace the current poster with this ${poster.source} poster (${poster.width}×${poster.height})?
              
The poster will be uploaded without any badges. You can apply badges separately using the "Apply Badges" button if desired.`;
    });
    
    // Methods
    const fetchPosterSources = async () => {
      isLoading.value = true;
      error.value = null;
      
      try {
        const response = await fetch(`/api/poster-manager/item/${props.item.id}/poster-sources`);
        const data = await response.json();
        
        if (data.success) {
          posterSources.value = data.sources || [];
        } else {
          error.value = data.message || 'Failed to fetch poster sources';
        }
      } catch (err) {
        error.value = 'Network error while fetching poster sources';
        console.error('Error fetching poster sources:', err);
      } finally {
        isLoading.value = false;
      }
    };
    
    const selectPoster = (poster) => {
      selectedPoster.value = poster;
    };
    
    const confirmSelection = () => {
      if (!selectedPoster.value) return;
      showConfirmDialog.value = true;
    };
    
    const replaceWithSelectedPoster = async () => {
      if (!selectedPoster.value) return;
      
      showConfirmDialog.value = false;
      isProcessing.value = true;
      
      try {
        const response = await fetch(`/api/poster-manager/item/${props.item.id}/replace-poster`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            poster_data: selectedPoster.value,
            badges: [] // Always empty - no badges applied
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          // Emit success event with job ID for parent to track
          emit('poster-replaced', {
            jobId: data.jobId,
            posterSource: selectedPoster.value.source,
            badges: [] // No badges applied
          });
          
          // Close modal
          emit('close');
        } else {
          error.value = data.message || 'Failed to start poster replacement';
        }
      } catch (err) {
        error.value = 'Network error while replacing poster';
        console.error('Error replacing poster:', err);
      } finally {
        isProcessing.value = false;
      }
    };
    
    const handleImageError = (event) => {
      event.target.src = '/images/professor_relaxing.png';
    };
    
    // Initialize
    onMounted(() => {
      fetchPosterSources();
    });
    
    return {
      isLoading,
      isProcessing,
      error,
      posterSources,
      selectedPoster,
      showConfirmDialog,
      selectedSource,
      selectedLanguage,
      sortBy,
      availableSources,
      availableLanguages,
      filteredPosters,
      confirmMessage,
      selectPoster,
      confirmSelection,
      replaceWithSelectedPoster,
      handleImageError
    };
  }
}
</script>
