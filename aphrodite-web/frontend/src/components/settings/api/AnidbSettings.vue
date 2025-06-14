<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h3 class="card-title">AniDB API</h3>
      
      <div class="form-control w-full">
        <label class="label" for="anidb-username">
          <span class="label-text">Username</span>
        </label>
        <input 
          id="anidb-username" 
          :value="modelValue.username"
          @input="updateValue('username', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="Your AniDB username"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="anidb-password">
          <span class="label-text">Password</span>
        </label>
        <div class="relative">
          <input 
            id="anidb-password" 
            :type="showPassword ? 'text' : 'password'" 
            :value="modelValue.password"
            @input="updateValue('password', $event.target.value)"
            class="input input-bordered w-full pr-10"
            placeholder="Your AniDB password"
          />
          <button 
            type="button" 
            @click="showPassword = !showPassword" 
            class="absolute inset-y-0 right-0 pr-3 flex items-center btn btn-ghost btn-sm"
          >
            <!-- Eye Icon (when password is hidden) -->
            <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
            <!-- Eye Slash Icon (when password is visible) -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21" />
            </svg>
          </button>
        </div>
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="anidb-version">
          <span class="label-text">Version</span>
        </label>
        <input 
          id="anidb-version" 
          :value="modelValue.version"
          @input="updateValue('version', parseInt($event.target.value))"
          type="number" 
          min="1"
          class="input input-bordered w-full"
          placeholder="1"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="anidb-client-name">
          <span class="label-text">Client Name</span>
        </label>
        <input 
          id="anidb-client-name" 
          :value="modelValue.client_name"
          @input="updateValue('client_name', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="MyClientName"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="anidb-language">
          <span class="label-text">Language</span>
        </label>
        <input 
          id="anidb-language" 
          :value="modelValue.language"
          @input="updateValue('language', $event.target.value)"
          type="text" 
          class="input input-bordered w-full"
          placeholder="en"
        />
      </div>
      
      <div class="form-control w-full">
        <label class="label" for="anidb-cache">
          <span class="label-text">Cache Expiration (minutes)</span>
        </label>
        <input 
          id="anidb-cache" 
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
import { ref } from 'vue';
import TestConnectionButton from './TestConnectionButton.vue';

export default {
  name: 'AnidbSettings',
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
    const showPassword = ref(false);

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
      showPassword,
      updateValue,
      handleTest
    };
  }
};
</script>
