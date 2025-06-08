<template>
  <div v-if="isOpen" class="modal modal-open">
    <div class="modal-box max-w-md">
      <!-- Header with Icon -->
      <div class="flex items-center gap-3 mb-4">
        <!-- Success Icon -->
        <div v-if="variant === 'success'" class="flex-shrink-0">
          <div class="w-10 h-10 rounded-full bg-success/20 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-success" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        
        <!-- Error Icon -->
        <div v-else-if="variant === 'error'" class="flex-shrink-0">
          <div class="w-10 h-10 rounded-full bg-error/20 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-error" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
        </div>
        
        <!-- Warning Icon -->
        <div v-else-if="variant === 'warning'" class="flex-shrink-0">
          <div class="w-10 h-10 rounded-full bg-warning/20 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-warning" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
        </div>
        
        <!-- Info Icon -->
        <div v-else class="flex-shrink-0">
          <div class="w-10 h-10 rounded-full bg-info/20 flex items-center justify-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-info" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
        
        <div class="flex-1">
          <h3 class="font-bold text-lg">{{ title }}</h3>
        </div>
      </div>
      
      <!-- Content -->
      <div class="mb-6">
        <p class="text-sm">{{ message }}</p>
      </div>
      
      <!-- Actions -->
      <div class="modal-action">
        <button 
          @click="handleClose" 
          class="btn btn-primary"
        >
          {{ buttonText || 'OK' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotificationModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      required: true
    },
    message: {
      type: String,
      required: true
    },
    variant: {
      type: String,
      default: 'info', // success, error, warning, info
      validator: (value) => ['success', 'error', 'warning', 'info'].includes(value)
    },
    buttonText: {
      type: String,
      default: 'OK'
    },
    autoClose: {
      type: Number,
      default: 0 // 0 = no auto close, otherwise milliseconds
    }
  },
  emits: ['close'],
  mounted() {
    if (this.autoClose > 0) {
      setTimeout(() => {
        this.handleClose()
      }, this.autoClose)
    }
  },
  methods: {
    handleClose() {
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
/* DaisyUI handles modal positioning automatically */
</style>
