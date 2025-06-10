<template>
  <div class="form-control w-full">
    <button 
      type="button" 
      @click="handleTest" 
      class="btn btn-success btn-outline"
      :disabled="testing"
    >
      <span v-if="testing" class="loading loading-spinner loading-sm"></span>
      {{ testing ? 'Testing...' : 'Test Connection' }}
    </button>
    <div v-if="status" class="mt-2">
      <div v-if="status.success" class="alert alert-success">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ status.message }}</span>
      </div>
      <div v-else class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ status.message }}</span>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'TestConnectionButton',
  props: {
    testing: {
      type: Boolean,
      default: false
    },
    status: {
      type: Object,
      default: null
    }
  },
  emits: ['test'],
  setup(props, { emit }) {
    const handleTest = () => {
      emit('test');
    };

    return {
      handleTest
    };
  }
};
</script>
