<template>
  <div v-if="show" class="modal modal-open">
    <div class="modal-box">
      <h3 class="font-bold text-lg">{{ title }}</h3>
      <p class="py-4">{{ message }}</p>
      
      <!-- Loading state -->
      <div v-if="isProcessing" class="flex items-center justify-center py-4">
        <span class="loading loading-spinner loading-md mr-2"></span>
        <span>Processing...</span>
      </div>
      
      <!-- Results display -->
      <div v-if="results && !isProcessing" class="mb-4">
        <div class="stats stats-vertical sm:stats-horizontal w-full mb-4">
          <div class="stat">
            <div class="stat-title">Total Items</div>
            <div class="stat-value text-sm">{{ results.total_items }}</div>
          </div>
          <div class="stat">
            <div class="stat-title">Successful</div>
            <div class="stat-value text-sm text-success">{{ results.successful_items }}</div>
          </div>
          <div class="stat">
            <div class="stat-title">Failed</div>
            <div class="stat-value text-sm text-error">{{ results.failed_items }}</div>
          </div>
        </div>
        
        <!-- Detailed results (if there are failures) -->
        <div v-if="results.failed_items > 0" class="collapse collapse-arrow bg-base-200">
          <input type="checkbox" />
          <div class="collapse-title text-sm font-medium">
            View details ({{ results.failed_items }} failures)
          </div>
          <div class="collapse-content">
            <div class="max-h-40 overflow-y-auto">
              <div v-for="result in results.results" :key="result.item_id" class="text-xs py-1">
                <div v-if="!result.success" class="flex items-center text-error">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  {{ result.item_name }}: {{ result.error || 'Unknown error' }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <div class="modal-action">
        <button 
          v-if="!isProcessing && !results" 
          class="btn btn-error" 
          @click="handleCancel"
        >
          Cancel
        </button>
        <button 
          v-if="!isProcessing && !results" 
          class="btn btn-success" 
          @click="handleConfirm"
          :disabled="isProcessing"
        >
          {{ confirmText }}
        </button>
        <button 
          v-if="results || (!isProcessing && !confirmText)" 
          class="btn" 
          @click="handleClose"
        >
          {{ results ? 'Close' : 'OK' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue';

export default {
  name: 'TagManagementModal',
  props: {
    show: {
      type: Boolean,
      default: false
    },
    action: {
      type: String,
      default: 'add' // 'add' or 'remove'
    },
    selectedCount: {
      type: Number,
      default: 0
    }
  },
  emits: ['confirm', 'cancel', 'close'],
  setup(props, { emit }) {
    const isProcessing = ref(false);
    const results = ref(null);
    
    const title = computed(() => {
      if (results.value) {
        return 'Tag Management Complete';
      }
      const actionText = props.action === 'add' ? 'Add' : 'Remove';
      return `${actionText} Aphrodite Tags`;
    });
    
    const message = computed(() => {
      if (results.value) {
        const actionText = props.action === 'add' ? 'added to' : 'removed from';
        return `Tags have been ${actionText} the selected items.`;
      }
      
      const actionText = props.action === 'add' ? 'add' : 'remove';
      const preposition = props.action === 'add' ? 'to' : 'from';
      return `Are you sure you want to ${actionText} the aphrodite-overlay tag ${preposition} ${props.selectedCount} selected item(s)?`;
    });
    
    const confirmText = computed(() => {
      const actionText = props.action === 'add' ? 'Add Tags' : 'Remove Tags';
      return actionText;
    });
    
    const handleConfirm = () => {
      isProcessing.value = true;
      emit('confirm');
    };
    
    const handleCancel = () => {
      emit('cancel');
    };
    
    const handleClose = () => {
      isProcessing.value = false;
      results.value = null;
      emit('close');
    };
    
    const showResults = (resultData) => {
      isProcessing.value = false;
      results.value = resultData;
    };
    
    const showProcessing = () => {
      isProcessing.value = true;
      results.value = null;
    };
    
    return {
      isProcessing,
      results,
      title,
      message,
      confirmText,
      handleConfirm,
      handleCancel,
      handleClose,
      showResults,
      showProcessing
    };
  }
}
</script>
