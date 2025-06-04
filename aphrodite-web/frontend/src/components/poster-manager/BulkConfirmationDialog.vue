<template>
  <div class="modal modal-open">
    <div class="modal-box w-11/12 max-w-2xl">
      <!-- Modal Header -->
      <h3 class="font-bold text-lg mb-4">Apply Badges to {{ selectedCount }} Posters</h3>
      
      <!-- Selected Posters Preview -->
      <div class="mb-6">
        <h4 class="font-semibold mb-3">Selected Posters:</h4>
        <div class="max-h-32 overflow-y-auto bg-base-200 rounded-lg p-3">
          <div class="grid grid-cols-1 gap-1 text-sm">
            <div v-for="item in selectedItems.slice(0, 10)" :key="item.id" class="flex items-center gap-2">
              <span class="w-2 h-2 bg-primary rounded-full flex-shrink-0"></span>
              <span class="truncate">{{ item.name }}</span>
              <span class="text-xs opacity-60">{{ item.year }}</span>
            </div>
            <div v-if="selectedItems.length > 10" class="text-xs opacity-60 mt-1">
              ... and {{ selectedItems.length - 10 }} more items
            </div>
          </div>
        </div>
      </div>
      
      <!-- Badge Selection -->
      <div class="mb-6">
        <h4 class="font-semibold mb-3">Select Badges to Apply:</h4>
        
        <!-- Badge Options -->
        <div class="space-y-3">
          <label v-for="badge in availableBadges" :key="badge.key" class="flex items-center gap-3 cursor-pointer p-3 rounded-lg border border-base-300 hover:bg-base-100 transition-colors">
            <input 
              type="checkbox" 
              class="checkbox checkbox-primary" 
              :checked="selectedBadges.includes(badge.key)"
              @change="toggleBadge(badge.key)"
            />
            <div class="flex-1">
              <div class="font-medium">{{ badge.label }}</div>
              <div class="text-sm opacity-60">{{ badge.description }}</div>
            </div>
          </label>
        </div>
        
        <!-- No badges warning -->
        <div v-if="selectedBadges.length === 0" class="alert alert-warning mt-3">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <span>Please select at least one badge type to apply.</span>
        </div>
      </div>
      
      <!-- Processing Info -->
      <div class="bg-info/10 border border-info/20 rounded-lg p-4 mb-6">
        <div class="flex items-start gap-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-info flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div class="text-sm">
            <div class="font-medium text-info">Processing Information</div>
            <div class="mt-1 opacity-80">
              • Only posters without existing badges will be processed<br>
              • Posters with badges will be skipped (use revert first if needed)<br>
              • Processing will run in the background and you can track progress
            </div>
          </div>
        </div>
      </div>
      
      <!-- Modal Actions -->
      <div class="modal-action">
        <button 
          class="btn btn-ghost" 
          @click="$emit('cancel')"
          :disabled="isProcessing"
        >
          Cancel
        </button>
        <button 
          class="btn btn-primary"
          @click="handleConfirm"
          :disabled="isProcessing || selectedBadges.length === 0"
        >
          <span v-if="isProcessing" class="loading loading-spinner loading-sm"></span>
          {{ isProcessing ? 'Starting...' : `Apply to ${selectedCount} Posters` }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'

export default {
  name: 'BulkConfirmationDialog',
  props: {
    selectedCount: {
      type: Number,
      required: true
    },
    selectedItems: {
      type: Array,
      required: true
    }
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const isProcessing = ref(false)
    
    const availableBadges = ref([
      { key: 'audio', label: 'Audio Codec', description: 'DTS-X, Atmos, TrueHD, etc.' },
      { key: 'resolution', label: 'Resolution', description: '4K, 1080p, HDR, etc.' },
      { key: 'review', label: 'Reviews', description: 'IMDb, TMDb ratings' },
      { key: 'awards', label: 'Awards', description: 'Crunchyroll, festival awards' }
    ])
    
    const selectedBadges = ref(['audio', 'resolution', 'review', 'awards'])
    
    const toggleBadge = (badgeKey) => {
      const index = selectedBadges.value.indexOf(badgeKey)
      if (index === -1) {
        selectedBadges.value.push(badgeKey)
      } else {
        selectedBadges.value.splice(index, 1)
      }
    }
    
    const handleConfirm = () => {
      if (selectedBadges.value.length === 0) return
      
      isProcessing.value = true
      emit('confirm', selectedBadges.value)
    }
    
    return {
      isProcessing,
      availableBadges,
      selectedBadges,
      toggleBadge,
      handleConfirm
    }
  }
}
</script>
