<template>
  <div class="modal modal-open">
    <div class="modal-box w-96">
      <!-- Modal Header -->
      <h3 class="font-bold text-lg mb-4">{{ title }}</h3>
      
      <!-- Content -->
      <p class="py-4" :class="typeClasses">{{ message }}</p>
      
      <!-- Badge Selection (if enabled) -->
      <div v-if="showBadgeSelection" class="mb-4">
        <h4 class="font-semibold mb-3">Select Badges to Apply:</h4>
        
        <!-- No Badges Option -->
        <label class="flex items-center gap-2 cursor-pointer mb-3 p-2 rounded border" :class="selectedBadges.length === 0 ? 'bg-base-200 border-primary' : 'border-base-300'">
          <input 
            type="radio" 
            name="badge-option"
            class="radio radio-primary radio-sm" 
            :checked="selectedBadges.length === 0"
            @change="selectNoBadges"
          />
          <div>
            <span class="text-sm font-medium">No Badges (Original Poster Only)</span>
            <div class="text-xs opacity-60">Upload the poster without any badges applied</div>
          </div>
        </label>
        
        <!-- Custom Badges Option -->
        <label class="flex items-center gap-2 cursor-pointer mb-2 p-2 rounded border" :class="selectedBadges.length > 0 ? 'bg-base-200 border-primary' : 'border-base-300'">
          <input 
            type="radio" 
            name="badge-option"
            class="radio radio-primary radio-sm" 
            :checked="selectedBadges.length > 0"
            @change="enableCustomBadges"
          />
          <span class="text-sm font-medium">Apply Selected Badges</span>
        </label>
        
        <!-- Badge Checkboxes (only shown when custom badges selected) -->
        <div v-if="selectedBadges.length > 0 || customBadgesEnabled" class="ml-6 space-y-2">
          <label v-for="badge in availableBadges" :key="badge.key" class="flex items-center gap-2 cursor-pointer">
            <input 
              type="checkbox" 
              class="checkbox checkbox-primary checkbox-sm" 
              :checked="selectedBadges.includes(badge.key)"
              @change="toggleBadge(badge.key)"
            />
            <span class="text-sm">{{ badge.label }}</span>
            <span class="text-xs opacity-60">{{ badge.description }}</span>
          </label>
        </div>
      </div>
      
      <!-- Warning Icon for Destructive Actions -->
      <div v-if="type === 'warning'" class="flex items-center gap-2 mb-4 text-warning">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <span class="text-sm font-medium">This action cannot be undone!</span>
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
          class="btn"
          :class="confirmButtonClass"
          @click="handleConfirm"
          :disabled="isProcessing"
        >
          <span v-if="isProcessing" class="loading loading-spinner loading-sm"></span>
          {{ isProcessing ? 'Processing...' : confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, ref, watch } from 'vue'

export default {
  name: 'ConfirmationDialog',
  props: {
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      required: true
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    type: {
      type: String,
      default: 'info', // 'info', 'warning', 'success', 'error'
      validator: (value) => ['info', 'warning', 'success', 'error'].includes(value)
    },
    isProcessing: {
      type: Boolean,
      default: false
    },
    showBadgeSelection: {
      type: Boolean,
      default: false
    },
    availableBadges: {
      type: Array,
      default: () => []
    },
    defaultSelectedBadges: {
      type: Array,
      default: () => []
    }
  },
  emits: ['confirm', 'cancel'],
  setup(props, { emit }) {
    const selectedBadges = ref([...props.defaultSelectedBadges])
    const customBadgesEnabled = ref(props.defaultSelectedBadges.length > 0)
    
    // Watch for changes in defaultSelectedBadges prop
    watch(() => props.defaultSelectedBadges, (newBadges) => {
      selectedBadges.value = [...newBadges]
      customBadgesEnabled.value = newBadges.length > 0
    })
    
    const typeClasses = computed(() => {
      switch (props.type) {
        case 'warning':
          return 'text-warning'
        case 'error':
          return 'text-error'
        case 'success':
          return 'text-success'
        default:
          return ''
      }
    })
    
    const confirmButtonClass = computed(() => {
      switch (props.type) {
        case 'warning':
        case 'error':
          return 'btn-error'
        case 'success':
          return 'btn-success'
        default:
          return 'btn-primary'
      }
    })
    
    const toggleBadge = (badgeKey) => {
      const index = selectedBadges.value.indexOf(badgeKey)
      if (index === -1) {
        selectedBadges.value.push(badgeKey)
      } else {
        selectedBadges.value.splice(index, 1)
      }
      
      // If no badges left, switch to "no badges" mode
      if (selectedBadges.value.length === 0) {
        customBadgesEnabled.value = false
      }
    }
    
    const selectNoBadges = () => {
      selectedBadges.value = []
      customBadgesEnabled.value = false
    }
    
    const enableCustomBadges = () => {
      customBadgesEnabled.value = true
      // If no badges selected, select all by default
      if (selectedBadges.value.length === 0) {
        selectedBadges.value = [...props.defaultSelectedBadges]
      }
    }
    
    const handleConfirm = () => {
      if (props.showBadgeSelection) {
        emit('confirm', selectedBadges.value)
      } else {
        emit('confirm')
      }
    }
    
    return {
      selectedBadges,
      customBadgesEnabled,
      typeClasses,
      confirmButtonClass,
      toggleBadge,
      selectNoBadges,
      enableCustomBadges,
      handleConfirm
    }
  }
}
</script>
