<template>
  <div v-if="isOpen" class="modal modal-open">
    <div class="modal-box">
      <!-- Header -->
      <h3 class="font-bold text-lg mb-4">
        {{ title || 'Confirm Action' }}
      </h3>
      
      <!-- Content -->
      <div class="mb-6">
        <p class="text-sm">
          {{ message }}
        </p>
      </div>
      
      <!-- Actions -->
      <div class="modal-action">
        <button 
          @click="handleCancel" 
          class="btn btn-ghost"
          :disabled="loading"
        >
          {{ cancelText || 'Cancel' }}
        </button>
        <button 
          @click="handleConfirm" 
          class="btn"
          :class="confirmButtonClass"
          :disabled="loading"
        >
          <span v-if="loading" class="loading loading-spinner loading-sm mr-2"></span>
          {{ confirmText || 'Confirm' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ConfirmationModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    title: {
      type: String,
      default: 'Confirm Action'
    },
    message: {
      type: String,
      required: true
    },
    confirmText: {
      type: String,
      default: 'Confirm'
    },
    cancelText: {
      type: String,
      default: 'Cancel'
    },
    variant: {
      type: String,
      default: 'primary', // primary, error, warning, success
      validator: (value) => ['primary', 'error', 'warning', 'success'].includes(value)
    },
    loading: {
      type: Boolean,
      default: false
    }
  },
  emits: ['confirm', 'cancel', 'close'],
  computed: {
    confirmButtonClass() {
      switch (this.variant) {
        case 'error':
          return 'btn-error'
        case 'warning':
          return 'btn-warning'
        case 'success':
          return 'btn-success'
        default:
          return 'btn-primary'
      }
    }
  },
  methods: {
    handleConfirm() {
      this.$emit('confirm')
    },
    handleCancel() {
      this.$emit('cancel')
      this.$emit('close')
    }
  }
}
</script>

<style scoped>
/* DaisyUI handles modal positioning automatically */
</style>
