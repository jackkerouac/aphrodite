<template>
  <div class="bg-white shadow rounded-lg p-4 border border-gray-200">
    <h3 class="text-lg font-medium mb-3">TMDB API</h3>
    
    <div class="grid grid-cols-1 gap-4">
      <div class="form-group">
        <label for="tmdb-api-key" class="block text-sm font-medium text-gray-700 mb-1">API Key</label>
        <input 
          id="tmdb-api-key" 
          :value="modelValue.api_key"
          @input="updateValue('api_key', $event.target.value)"
          type="text" 
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="Your TMDB API key"
        />
      </div>
      
      <div class="form-group">
        <label for="tmdb-cache" class="block text-sm font-medium text-gray-700 mb-1">Cache Expiration (minutes)</label>
        <input 
          id="tmdb-cache" 
          :value="modelValue.cache_expiration"
          @input="updateValue('cache_expiration', parseInt($event.target.value))"
          type="number" 
          min="0"
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="60"
        />
      </div>
      
      <div class="form-group">
        <label for="tmdb-language" class="block text-sm font-medium text-gray-700 mb-1">Language</label>
        <input 
          id="tmdb-language" 
          :value="modelValue.language"
          @input="updateValue('language', $event.target.value)"
          type="text" 
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="en"
        />
      </div>
      
      <div class="form-group">
        <label for="tmdb-region" class="block text-sm font-medium text-gray-700 mb-1">Region (optional)</label>
        <input 
          id="tmdb-region" 
          :value="modelValue.region"
          @input="updateValue('region', $event.target.value)"
          type="text" 
          class="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          placeholder="US"
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
  name: 'TmdbSettings',
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
