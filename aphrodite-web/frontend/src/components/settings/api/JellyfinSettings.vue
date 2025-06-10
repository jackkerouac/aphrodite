<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h3 class="card-title">Jellyfin Connection</h3>
      
      <div class="form-control w-full">
        <label class="label" for="jellyfin-url">
          <span class="label-text">Server URL</span>
        </label>
        <input 
          id="jellyfin-url" 
          :value="modelValue.url"
          @input="updateValue('url', $event.target.value)"
          @change="console.log('DEBUG: URL input changed to:', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="https://jellyfin.example.com"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="jellyfin-api-key">
          <span class="label-text">API Key</span>
        </label>
        <input 
          id="jellyfin-api-key" 
          :value="modelValue.api_key"
          @input="updateValue('api_key', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="Your Jellyfin API key"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="jellyfin-user-id">
          <span class="label-text">User ID</span>
        </label>
        <input 
          id="jellyfin-user-id" 
          :value="modelValue.user_id"
          @input="updateValue('user_id', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="Your Jellyfin user ID"
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
  name: 'JellyfinSettings',
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
      console.log(`DEBUG: JellyfinSettings.updateValue called with key: ${key}, value: ${value}`);
      console.log('DEBUG: Current modelValue before update:', props.modelValue);
      
      const newValue = {
        ...props.modelValue,
        [key]: value
      };
      
      console.log('DEBUG: New value to emit:', newValue);
      emit('update:modelValue', newValue);
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
