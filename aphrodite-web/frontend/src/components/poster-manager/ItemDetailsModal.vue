<template>
  <div class="modal modal-open">
    <div class="modal-box w-11/12 max-w-4xl">
      <!-- Modal Header -->
      <div class="flex justify-between items-center mb-4">
        <h3 class="font-bold text-lg">Poster Details</h3>
        <button class="btn btn-sm btn-circle btn-ghost" @click="$emit('close')">✕</button>
      </div>

      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg"></span>
      </div>

      <!-- Content -->
      <div v-else class="space-y-6">
        <!-- Item Information -->
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <!-- Poster Image -->
          <div class="space-y-4">
            <div class="relative">
              <img 
                :src="item.poster_url || '/images/professor_relaxing.png'"
                :alt="item.name"
                class="w-full rounded-lg shadow-lg"
                @error="handleImageError"
              />
              <!-- Status Badge -->
              <div class="absolute top-2 right-2">
                <div 
                  class="badge badge-lg"
                  :class="posterStatus?.has_modified ? 'badge-primary' : 'badge-ghost'"
                >
                  {{ posterStatus?.has_modified ? 'Badged' : 'Original' }}
                </div>
              </div>
            </div>

            <!-- Poster Information -->
            <div class="card bg-base-200">
              <div class="card-body p-4">
                <h4 class="card-title text-sm">Poster Information</h4>
                <div class="text-sm space-y-1">
                  <div><strong>Source:</strong> {{ posterStatus?.current_source || 'Unknown' }}</div>
                  <div v-if="posterStatus?.has_original">
                    <strong>Original:</strong> Available
                  </div>
                  <div v-if="posterStatus?.has_modified">
                    <strong>Modified:</strong> {{ formatDate(posterStatus.modified_created) }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Item Details -->
          <div class="space-y-4">
            <div>
              <h2 class="text-2xl font-bold">{{ item.name }}</h2>
              <div class="flex flex-wrap gap-2 mt-2">
                <div class="badge badge-outline">{{ item.type }}</div>
                <div v-if="item.year" class="badge badge-outline">{{ item.year }}</div>
                <div v-for="genre in (item.genres || []).slice(0, 3)" :key="genre" class="badge badge-outline">
                  {{ genre }}
                </div>
              </div>
            </div>

            <div v-if="item.overview" class="text-sm opacity-80">
              {{ item.overview }}
            </div>

            <!-- Badge History -->
            <div v-if="badgeHistory" class="card bg-base-200">
              <div class="card-body p-4">
                <h4 class="card-title text-sm">Badge History</h4>
                <div class="text-sm space-y-1">
                  <div v-if="badgeHistory.last_processed">
                    <strong>Last Processed:</strong> {{ formatDate(badgeHistory.last_processed) }}
                  </div>
                  <div>
                    <strong>Processing Count:</strong> {{ badgeHistory.processing_count }}
                  </div>
                  <div v-if="badgeHistory.badges_applied && badgeHistory.badges_applied.length > 0">
                    <strong>Applied Badges:</strong> {{ badgeHistory.badges_applied.join(', ') }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="divider">Actions</div>
        <div class="flex flex-wrap gap-3">
          <button 
            class="btn btn-primary"
            :disabled="isProcessing"
            @click="reprocessItem"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ isProcessing ? 'Processing...' : 'Re-apply Badges' }}
          </button>

          <button 
            class="btn btn-secondary"
            :disabled="!posterStatus?.has_modified || isProcessing"
            @click="revertToOriginal"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
            </svg>
            Revert to Original
          </button>

          <button 
            class="btn btn-outline"
            @click="fetchNewPoster"
            :disabled="isProcessing"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
            </svg>
            Fetch New Poster
          </button>

          <button 
            class="btn btn-outline"
            @click="uploadCustomPoster"
            :disabled="isProcessing"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            Upload Custom
          </button>
        </div>

        <!-- Processing Status -->
        <div v-if="actionMessage" class="alert" :class="actionMessage.type === 'success' ? 'alert-success' : 'alert-error'">
          <div>
            <svg v-if="actionMessage.type === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span>{{ actionMessage.text }}</span>
          </div>
        </div>
      </div>

      <!-- Modal Actions -->
      <div class="modal-action">
        <button class="btn" @click="$emit('close')">Close</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';

export default {
  name: 'ItemDetailsModal',
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'item-updated'],
  setup(props) {
    const isLoading = ref(false);
    const isProcessing = ref(false);
    const posterStatus = ref(null);
    const badgeHistory = ref(null);
    const actionMessage = ref(null);

    // Methods
    const loadItemDetails = async () => {
      isLoading.value = true;
      try {
        const response = await fetch(`/api/poster-manager/item/${props.item.id}/details`);
        const data = await response.json();
        
        if (data.success) {
          posterStatus.value = data.poster_status;
          badgeHistory.value = data.badge_history;
        } else {
          console.error('Error loading item details:', data.message);
        }
      } catch (error) {
        console.error('Error loading item details:', error);
      } finally {
        isLoading.value = false;
      }
    };

    const reprocessItem = async () => {
      isProcessing.value = true;
      actionMessage.value = null;
      
      try {
        // This would call the existing process API
        showActionMessage('Re-processing functionality will be implemented in Phase 2', 'info');
      } catch (error) {
        showActionMessage('Error re-processing item', 'error');
      } finally {
        isProcessing.value = false;
      }
    };

    const revertToOriginal = async () => {
      isProcessing.value = true;
      actionMessage.value = null;
      
      try {
        // This would call a revert API
        showActionMessage('Revert functionality will be implemented in Phase 2', 'info');
      } catch (error) {
        showActionMessage('Error reverting poster', 'error');
      } finally {
        isProcessing.value = false;
      }
    };

    const fetchNewPoster = () => {
      showActionMessage('External poster fetching will be implemented in Phase 3', 'info');
    };

    const uploadCustomPoster = () => {
      showActionMessage('Custom poster upload will be implemented in Phase 4', 'info');
    };

    const showActionMessage = (text, type = 'success') => {
      actionMessage.value = { text, type };
      setTimeout(() => {
        actionMessage.value = null;
      }, 5000);
    };

    const formatDate = (dateString) => {
      if (!dateString) return 'Unknown';
      return new Date(dateString).toLocaleString();
    };

    const handleImageError = (event) => {
      event.target.src = '/images/professor_relaxing.png';
    };

    // Load details on mount
    onMounted(() => {
      loadItemDetails();
    });

    return {
      isLoading,
      isProcessing,
      posterStatus,
      badgeHistory,
      actionMessage,
      reprocessItem,
      revertToOriginal,
      fetchNewPoster,
      uploadCustomPoster,
      formatDate,
      handleImageError
    };
  }
}
</script>
