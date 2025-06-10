<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h3 class="card-title">OMDB API</h3>
      
      <div class="form-control w-full">
        <label class="label" for="omdb-api-key">
          <span class="label-text">API Key</span>
        </label>
        <input 
          id="omdb-api-key" 
          :value="modelValue.api_key"
          @input="updateValue('api_key', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="Your OMDB API key"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="omdb-cache">
          <span class="label-text">Cache Expiration (minutes)</span>
        </label>
        <input 
          id="omdb-cache" 
          :value="modelValue.cache_expiration"
          @input="updateValue('cache_expiration', parseInt($event.target.value))"
          type="number" 
          min="0"
          class="input input-bordered w-full"
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
