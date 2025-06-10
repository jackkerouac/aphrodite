<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h3 class="card-title">TMDB API</h3>
      
      <div class="form-control w-full">
        <label class="label" for="tmdb-api-key">
          <span class="label-text">API Key</span>
        </label>
        <input 
          id="tmdb-api-key" 
          :value="modelValue.api_key"
          @input="updateValue('api_key', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="Your TMDB API key"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="tmdb-cache">
          <span class="label-text">Cache Expiration (minutes)</span>
        </label>
        <input 
          id="tmdb-cache" 
          :value="modelValue.cache_expiration"
          @input="updateValue('cache_expiration', parseInt($event.target.value))"
          type="number" 
          min="0"
          class="input input-bordered w-full"
          placeholder="60"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="tmdb-language">
          <span class="label-text">Language</span>
        </label>
        <input 
          id="tmdb-language" 
          :value="modelValue.language"
          @input="updateValue('language', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="en"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="tmdb-region">
          <span class="label-text">Region (optional)</span>
        </label>
        <input 
          id="tmdb-region" 
          :value="modelValue.region"
          @input="updateValue('region', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
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
