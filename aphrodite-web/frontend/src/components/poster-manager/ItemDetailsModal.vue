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
                :src="itemData.poster_url || '/images/professor_relaxing.png'"
                :alt="itemData.name"
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
                  <div v-if="posterStatus?.can_revert !== undefined">
                    <strong>Can Revert:</strong> {{ posterStatus.can_revert ? 'Yes' : 'No' }}
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Item Details -->
          <div class="space-y-4">
            <div>
              <h2 class="text-2xl font-bold">{{ itemData.name }}</h2>
              <div class="flex flex-wrap gap-2 mt-2">
                <div class="badge badge-outline">{{ itemData.type }}</div>
                <div v-if="itemData.year" class="badge badge-outline">{{ itemData.year }}</div>
                <div v-for="genre in (itemData.genres || []).slice(0, 3)" :key="genre" class="badge badge-outline">
                  {{ genre }}
                </div>
              </div>
            </div>

            <div v-if="itemData.overview" class="text-sm opacity-80">
              {{ itemData.overview }}
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
            :disabled="isProcessing || posterStatus?.has_badges"
            @click="showReprocessConfirmation"
            :title="posterStatus?.has_badges ? 'Item already has badges. Use revert first to re-apply badges.' : 'Apply badges to this poster'"
          >
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            {{ isProcessing ? 'Processing...' : 'Re-apply Badges' }}
          </button>

          <button 
            class="btn btn-secondary"
            :disabled="!posterStatus?.can_revert || isProcessing"
            @click="showRevertConfirmation"
            :title="posterStatus?.can_revert ? 'Remove badges and restore original poster' : 'Cannot revert: no badges or original poster not found'"
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
        <div v-if="actionMessage" class="alert" :class="actionMessage.type === 'success' ? 'alert-success' : actionMessage.type === 'error' ? 'alert-error' : 'alert-info'">
          <div>
            <svg v-if="actionMessage.type === 'success'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="actionMessage.type === 'error'" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
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

  <!-- Confirmation Dialogs -->
  <ConfirmationDialog
    v-if="showRevertDialog"
    title="Revert to Original Poster"
    message="This will remove all badges and restore the original poster. This action cannot be undone."
    confirm-text="Revert"
    type="warning"
    :is-processing="isProcessing"
    @confirm="revertToOriginal"
    @cancel="showRevertDialog = false"
  />

  <ConfirmationDialog
    v-if="showReprocessDialog"
    title="Apply Badges"
    message="Select which badges to apply to this poster:"
    confirm-text="Apply Selected Badges"
    type="info"
    :is-processing="isProcessing"
    :show-badge-selection="true"
    :available-badges="availableBadges"
    :default-selected-badges="defaultSelectedBadges"
    @confirm="reprocessItem"
    @cancel="showReprocessDialog = false"
  />

  <!-- Poster Search Modal -->
  <PosterSearchModal
    v-if="showPosterSearchModal"
    :item="itemData"
    @close="showPosterSearchModal = false"
    @poster-replaced="handlePosterReplaced"
  />
</template>

<script>
import { ref, onMounted } from 'vue';
import ConfirmationDialog from './ConfirmationDialog.vue';
import PosterSearchModal from './PosterSearchModal.vue';

export default {
  name: 'ItemDetailsModal',
  components: {
    ConfirmationDialog,
    PosterSearchModal
  },
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  emits: ['close', 'item-updated'],
  setup(props, { emit }) {
    const isLoading = ref(false);
    const isProcessing = ref(false);
    const posterStatus = ref(null);
    const badgeHistory = ref(null);
    const actionMessage = ref(null);
    const showRevertDialog = ref(false);
    const showReprocessDialog = ref(false);
    const showPosterSearchModal = ref(false);
    const currentJobId = ref(null);
    const jobCheckInterval = ref(null);
    const itemData = ref({ ...props.item }); // Create reactive copy of item data
    
    // Badge selection for reprocessing
    const availableBadges = ref([
      { key: 'audio', label: 'Audio Codec', description: 'DTS-X, Atmos, TrueHD, etc.' },
      { key: 'resolution', label: 'Resolution', description: '4K, 1080p, HDR, etc.' },
      { key: 'review', label: 'Reviews', description: 'IMDb, TMDb ratings' },
      { key: 'awards', label: 'Awards', description: 'Crunchyroll, festival awards' }
    ]);
    const defaultSelectedBadges = ref(['audio', 'resolution', 'review', 'awards']);

    // Methods
    const loadItemDetails = async () => {
      isLoading.value = true;
      try {
        const response = await fetch(`/api/poster-manager/item/${props.item.id}/details`);
        const data = await response.json();
        
        if (data.success) {
          posterStatus.value = data.poster_status;
          badgeHistory.value = data.badge_history;
          
          // Update item data and add cache-busting to poster URL
          Object.assign(itemData.value, data.item);
          if (itemData.value.poster_url) {
            const baseUrl = itemData.value.poster_url.split('?')[0];
            const urlParams = new URLSearchParams(itemData.value.poster_url.split('?')[1] || '');
            urlParams.set('_t', Date.now().toString());
            itemData.value.poster_url = `${baseUrl}?${urlParams.toString()}`;
          }
        } else {
          console.error('Error loading item details:', data.message);
          showActionMessage('Error loading item details', 'error');
        }
      } catch (error) {
        console.error('Error loading item details:', error);
        showActionMessage('Error loading item details', 'error');
      } finally {
        isLoading.value = false;
      }
    };

    const showReprocessConfirmation = () => {
      if (posterStatus.value?.has_badges) {
        showActionMessage('Item already has badges. Use revert first if you want to re-apply badges.', 'error');
        return;
      }
      showReprocessDialog.value = true;
    };

    const showRevertConfirmation = () => {
      if (!posterStatus.value?.can_revert) {
        showActionMessage('Cannot revert: item has no badges or original poster not found', 'error');
        return;
      }
      showRevertDialog.value = true;
    };

    const reprocessItem = async (selectedBadges) => {
      showReprocessDialog.value = false;
      isProcessing.value = true;
      actionMessage.value = null;
      
      try {
        const response = await fetch(`/api/poster-manager/item/${props.item.id}/reprocess`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            badges: selectedBadges
          })
        });
        
        const data = await response.json();
        
        if (data.success) {
          currentJobId.value = data.jobId;
          const badgeList = selectedBadges.join(', ');
          showActionMessage(`Badge processing started for: ${badgeList}...`, 'info');
          startJobStatusCheck();
        } else {
          showActionMessage(data.message || 'Error starting badge processing', 'error');
          isProcessing.value = false;
        }
      } catch (error) {
        showActionMessage('Error starting badge processing', 'error');
        isProcessing.value = false;
      }
    };

    const revertToOriginal = async () => {
      showRevertDialog.value = false;
      isProcessing.value = true;
      actionMessage.value = null;
      
      try {
        const response = await fetch(`/api/poster-manager/item/${props.item.id}/revert`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          }
        });
        
        const data = await response.json();
        
        if (data.success) {
          currentJobId.value = data.jobId;
          showActionMessage('Revert process started...', 'info');
          startJobStatusCheck();
        } else {
          showActionMessage(data.message || 'Error starting revert process', 'error');
          isProcessing.value = false;
        }
      } catch (error) {
        showActionMessage('Error starting revert process', 'error');
        isProcessing.value = false;
      }
    };

    const startJobStatusCheck = () => {
      if (jobCheckInterval.value) {
        clearInterval(jobCheckInterval.value);
      }
      
      jobCheckInterval.value = setInterval(async () => {
        try {
          const response = await fetch(`/api/jobs/${currentJobId.value}`);
          const data = await response.json();
          
          if (data.success && data.job) {
            const job = data.job;
            
            if (job.status === 'success') {
              clearInterval(jobCheckInterval.value);
              showActionMessage('Operation completed successfully!', 'success');
              isProcessing.value = false;
              
              // Reload item details to reflect changes
              await loadItemDetails();
              
              // Emit event to parent to refresh the gallery
              emit('item-updated');
              
            } else if (job.status === 'failed') {
              clearInterval(jobCheckInterval.value);
              const errorMsg = job.result?.error || job.result?.message || 'Operation failed';
              showActionMessage(errorMsg, 'error');
              isProcessing.value = false;
            }
            // Continue polling if status is still 'queued' or 'running'
          }
        } catch (error) {
          console.error('Error checking job status:', error);
        }
      }, 2000); // Check every 2 seconds
    };

    const handlePosterReplaced = async (replacementData) => {
      showPosterSearchModal.value = false;
      isProcessing.value = true;
      currentJobId.value = replacementData.jobId;
      
      const badgeList = replacementData.badges.join(', ') || 'none';
      showActionMessage(
        `Poster replacement started from ${replacementData.posterSource} with badges: ${badgeList}...`, 
        'info'
      );
      
      startJobStatusCheck();
    };

    const fetchNewPoster = () => {
      showPosterSearchModal.value = true;
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

    // Cleanup on component unmount
    onMounted(() => {
      loadItemDetails();
      
      return () => {
        if (jobCheckInterval.value) {
          clearInterval(jobCheckInterval.value);
        }
      };
    });

    return {
      isLoading,
      isProcessing,
      posterStatus,
      badgeHistory,
      actionMessage,
      showRevertDialog,
      showReprocessDialog,
      showPosterSearchModal,
      availableBadges,
      defaultSelectedBadges,
      itemData,
      showReprocessConfirmation,
      showRevertConfirmation,
      reprocessItem,
      revertToOriginal,
      fetchNewPoster,
      uploadCustomPoster,
      handlePosterReplaced,
      formatDate,
      handleImageError
    };
  }
}
</script>
