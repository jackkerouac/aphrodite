<template>
  <div class="form-group">
    <button 
      type="button" 
      @click="handleTest" 
      class="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
      :disabled="testing"
    >
      {{ testing ? 'Testing...' : 'Test Connection' }}
    </button>
    <span v-if="status" :class="status.success ? 'text-green-600' : 'text-red-600'" class="ml-2">
      {{ status.message }}
    </span>
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
