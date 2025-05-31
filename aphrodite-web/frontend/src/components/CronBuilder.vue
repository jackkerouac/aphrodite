<template>
  <div class="cron-builder">
    <div class="form-control w-full">
      <label class="label">
        <span class="label-text font-medium">Schedule</span>
      </label>
      
      <!-- Preset Patterns -->
      <div class="mb-4">
        <label class="label">
          <span class="label-text text-sm">Quick Presets</span>
        </label>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
          <button 
            v-for="preset in presets" 
            :key="preset.value"
            type="button"
            class="btn btn-sm btn-outline"
            :class="{ 'btn-primary': cronExpression === preset.value }"
            @click="selectPreset(preset.value)"
          >
            {{ preset.label }}
          </button>
        </div>
      </div>
      
      <!-- Manual Cron Expression -->
      <div class="form-control">
        <label class="label">
          <span class="label-text text-sm">Cron Expression</span>
        </label>
        <input
          v-model="cronExpression"
          type="text"
          placeholder="0 2 * * *"
          class="input input-bordered w-full"
          :class="{ 'input-error': !isValid && cronExpression }"
          @input="validateAndEmit"
        />
        <label class="label">
          <span class="label-text-alt text-xs">Format: minute hour day month weekday</span>
        </label>
      </div>
      
      <!-- Validation Status -->
      <div v-if="cronExpression" class="mt-2">
        <div v-if="isValid" class="alert alert-success py-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm">{{ description }}</span>
        </div>
        <div v-else class="alert alert-error py-2">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-4 w-4" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span class="text-sm">Invalid cron expression</span>
        </div>
      </div>
      
      <!-- Help Text -->
      <div class="mt-4 text-sm opacity-70">
        <div class="collapse collapse-arrow">
          <input type="checkbox" />
          <div class="collapse-title text-sm font-medium">
            Cron Expression Help
          </div>
          <div class="collapse-content text-xs">
            <div class="space-y-2">
              <div><strong>Format:</strong> minute hour day month weekday</div>
              <div><strong>Examples:</strong></div>
              <div>• <code>0 2 * * *</code> - Every day at 2:00 AM</div>
              <div>• <code>0 */6 * * *</code> - Every 6 hours</div>
              <div>• <code>0 0 * * 0</code> - Every Sunday at midnight</div>
              <div>• <code>30 1 1 * *</code> - First day of every month at 1:30 AM</div>
              <div><strong>Special characters:</strong></div>
              <div>• <code>*</code> - Any value</div>
              <div>• <code>*/n</code> - Every n units</div>
              <div>• <code>n-m</code> - Range from n to m</div>
              <div>• <code>n,m</code> - Specific values n and m</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch } from 'vue'
import api from '@/api'

export default {
  name: 'CronBuilder',
  props: {
    modelValue: {
      type: String,
      default: ''
    }
  },
  emits: ['update:modelValue', 'valid'],
  setup(props, { emit }) {
    const cronExpression = ref(props.modelValue)
    const isValid = ref(false)
    const description = ref('')
    
    // Common cron presets
    const presets = ref([
      { label: 'Every Hour', value: '0 * * * *' },
      { label: 'Daily 2AM', value: '0 2 * * *' },
      { label: 'Weekly', value: '0 2 * * 0' },
      { label: 'Monthly', value: '0 2 1 * *' },
      { label: 'Every 6 Hours', value: '0 */6 * * *' },
      { label: 'Weekdays 2AM', value: '0 2 * * 1-5' },
      { label: 'Weekend 2AM', value: '0 2 * * 6,0' },
      { label: 'Twice Daily', value: '0 2,14 * * *' }
    ])
    
    // Watch for external changes to modelValue
    watch(() => props.modelValue, (newValue) => {
      cronExpression.value = newValue
      validateCron()
    })
    
    // Watch for changes to cronExpression
    watch(cronExpression, () => {
      validateAndEmit()
    })
    
    const selectPreset = (preset) => {
      cronExpression.value = preset
      validateAndEmit()
    }
    
    const validateCron = async () => {
      if (!cronExpression.value.trim()) {
        isValid.value = false
        description.value = ''
        return
      }
      
      try {
        const response = await api.schedules.validateCron(cronExpression.value)
        isValid.value = response.data.valid
        description.value = response.data.description || ''
      } catch (error) {
        console.error('Error validating cron:', error)
        isValid.value = false
        description.value = 'Unable to validate cron expression'
      }
    }
    
    const validateAndEmit = () => {
      validateCron()
      emit('update:modelValue', cronExpression.value)
      emit('valid', isValid.value)
    }
    
    // Initial validation
    if (cronExpression.value) {
      validateCron()
    }
    
    return {
      cronExpression,
      isValid,
      description,
      presets,
      selectPreset,
      validateAndEmit
    }
  }
}
</script>
