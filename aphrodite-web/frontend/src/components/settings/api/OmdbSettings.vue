<template>
  <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
    <h3 class="text-lg font-medium mb-3">OMDB API</h3>
    
    <div class="grid grid-cols-1 gap-4">
      <div class="form-group">
        <label for="omdb-api-key" class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
        <input 
          id="omdb-api-key" 
          :value="modelValue.api_key"
          @input="updateValue('api_key', $event.target.value)"
          type="text" 
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Your OMDB API key"
        />
      </div>
      
      <div class="form-group">
        <label for="omdb-cache" class="block text-sm font-medium text-gray-700 mb-1">Cache Expiration (minutes)</label>
        <input 
          id="omdb-cache" 
          :value="modelValue.cache_expiration"
          @input="updateValue('cache_expiration', parseInt($event.target.value))"
          type="number" 
          min="0"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="60"
        />
      </div>
      
      <TestConnectionButton 
        :testing="testing"
        :status="status"
        @test="handleTest"
      />
    </div>
  </div>
</template>

<script>
import TestConnectionButton from './TestConnectionButton.vue';

export default {
  name: 'OmdbSettings',
  components: {
    TestConnectionButton
  },
  props: {
    modelValue: {
      type: Object,
      required: true
    },
    testing: {
      type: Boolean,
      default: false
    },
    status: {
      type: Object,
      default: null
    }
  },
  emits: ['update:modelValue', 'test'],
  setup(props, { emit }) {
    const updateValue = (key, value) => {
      emit('update:modelValue', {
        ...props.modelValue,
        [key]: value
      });
    };

    const handleTest = () => {
      emit('test');
    };

    return {
      updateValue,
      handleTest
    };
  }
};
</script>
