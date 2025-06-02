<template>
  <div class="schedule-editor">
    <div class="card bg-base-100 shadow-lg">
      <div class="card-body">
        <h2 class="card-title mb-4">
          {{ isEditing ? 'Edit Schedule' : 'Create New Schedule' }}
        </h2>
        
        <form @submit.prevent="saveSchedule" class="space-y-6">
          <!-- Basic Information -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Schedule Name</span>
                <span class="label-text-alt text-error">*</span>
              </label>
              <input
                v-model="schedule.name"
                type="text"
                placeholder="e.g., Nightly Full Processing"
                class="input input-bordered"
                :class="{ 'input-error': errors.name }"
                required
              />
              <label v-if="errors.name" class="label">
                <span class="label-text-alt text-error">{{ errors.name }}</span>
              </label>
            </div>
            
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Timezone</span>
              </label>
              <select v-model="schedule.timezone" class="select select-bordered">
                <option value="UTC">UTC</option>
                <option value="America/New_York">Eastern Time</option>
                <option value="America/Chicago">Central Time</option>
                <option value="America/Denver">Mountain Time</option>
                <option value="America/Los_Angeles">Pacific Time</option>
                <option value="America/Toronto">Toronto</option>
                <option value="Europe/London">London</option>
                <option value="Europe/Paris">Paris</option>
                <option value="Asia/Tokyo">Tokyo</option>
              </select>
            </div>
          </div>
          
          <!-- Schedule Settings -->
          <div class="divider">Schedule</div>
          
          <CronBuilder 
            v-model="schedule.cron" 
            @valid="cronValid = $event"
          />
          
          <!-- Processing Options -->
          <div class="divider">Processing Options</div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <!-- Badge Types -->
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Badge Types</span>
              </label>
              <div class="space-y-2">
                <div class="form-control">
                  <label class="cursor-pointer label justify-start gap-2">
                    <input 
                      v-model="schedule.processing_options.audio_badges" 
                      type="checkbox" 
                      class="checkbox checkbox-primary"
                    />
                    <span class="label-text">Audio Badges</span>
                  </label>
                </div>
                <div class="form-control">
                  <label class="cursor-pointer label justify-start gap-2">
                    <input 
                      v-model="schedule.processing_options.resolution_badges" 
                      type="checkbox" 
                      class="checkbox checkbox-primary"
                    />
                    <span class="label-text">Resolution Badges</span>
                  </label>
                </div>
                <div class="form-control">
                  <label class="cursor-pointer label justify-start gap-2">
                    <input 
                      v-model="schedule.processing_options.review_badges" 
                      type="checkbox" 
                      class="checkbox checkbox-primary"
                    />
                    <span class="label-text">Review Badges</span>
                  </label>
                </div>
                <div class="form-control">
                  <label class="cursor-pointer label justify-start gap-2">
                    <input 
                      v-model="schedule.processing_options.awards_badges" 
                      type="checkbox" 
                      class="checkbox checkbox-primary"
                    />
                    <span class="label-text">Awards Badges</span>
                  </label>
                </div>
              </div>
            </div>
            
            <!-- Additional Options -->
            <div class="form-control">
              <label class="label">
                <span class="label-text font-medium">Additional Options</span>
              </label>
              <div class="space-y-2">
                <div class="form-control">
                  <label class="cursor-pointer label justify-start gap-2">
                    <input 
                      v-model="schedule.processing_options.force_refresh" 
                      type="checkbox" 
                      class="checkbox checkbox-secondary"
                    />
                    <span class="label-text">Force Refresh</span>
                  </label>
                  <div class="text-xs opacity-60 ml-6 -mt-1">
                    Re-process all items, even if already processed. Use when updating badge settings or fixing errors.
                  </div>
                </div>
                <div class="form-control">
                  <label class="cursor-pointer label justify-start gap-2">
                    <input 
                      v-model="schedule.enabled" 
                      type="checkbox" 
                      class="checkbox checkbox-accent"
                    />
                    <span class="label-text">Enable Schedule</span>
                  </label>
                  <div class="text-xs opacity-60 ml-6 -mt-1">
                    When enabled, schedule runs automatically. When disabled, schedule is saved but won't run automatically.
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- Target Directories -->
          <div class="form-control">
            <label class="label">
              <span class="label-text font-medium">Target Directories</span>
            </label>
            
            <!-- Jellyfin Libraries Section -->
            <div v-if="jellyfinLibraries.length > 0" class="mb-4">
              <div class="flex items-center justify-between mb-2">
                <span class="text-sm font-medium">Jellyfin Libraries</span>
                <button
                  type="button"
                  @click="refreshJellyfinLibraries"
                  class="btn btn-ghost btn-xs"
                  :disabled="loadingLibraries"
                >
                  <span v-if="loadingLibraries" class="loading loading-spinner loading-xs"></span>
                  <span v-else>↻</span>
                  Refresh
                </button>
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div 
                  v-for="library in jellyfinLibraries" 
                  :key="library.id"
                  class="form-control"
                >
                  <label class="cursor-pointer label justify-start gap-2 py-1">
                    <input 
                      type="checkbox"
                      class="checkbox checkbox-sm checkbox-primary"
                      :checked="isLibrarySelected(library)"
                      @change="toggleLibrary(library, $event.target.checked)"
                    />
                    <div class="flex flex-col">
                      <span class="label-text text-sm">{{ library.name }}</span>
                      <span v-if="library.type" class="label-text-alt text-xs opacity-60">
                        {{ library.type }}
                      </span>
                    </div>
                  </label>
                </div>
              </div>
              <div class="divider divider-horizontal text-xs opacity-50">OR</div>
            </div>
            
            <!-- Manual Directory Entry -->
            <div class="mb-2">
              <span class="text-sm font-medium">Manual Entry</span>
            </div>
            <div class="flex flex-wrap gap-2 mb-2">
              <div 
                v-for="(dir, index) in schedule.processing_options.target_directories" 
                :key="index"
                class="badge gap-2"
                :class="getDirectoryBadgeClass(dir)"
              >
                {{ dir }}
                <button 
                  type="button"
                  @click="removeDirectory(index)"
                  class="btn btn-ghost btn-xs"
                >
                  ×
                </button>
              </div>
            </div>
            <div class="input-group">
              <input
                v-model="newDirectory"
                type="text"
                placeholder="e.g., movies, tv, anime"
                class="input input-bordered flex-1"
                @keyup.enter="addDirectory"
              />
              <button 
                type="button"
                @click="addDirectory"
                class="btn btn-primary"
                :disabled="!newDirectory.trim()"
              >
                Add
              </button>
            </div>
            <label class="label">
              <span class="label-text-alt">
                Select from Jellyfin libraries above or manually add directory names
              </span>
            </label>
          </div>
          
          <!-- Actions -->
          <div class="card-actions justify-end gap-2 pt-4">
            <button 
              type="button" 
              @click="$emit('cancel')"
              class="btn btn-ghost"
            >
              Cancel
            </button>
            <button 
              type="submit" 
              class="btn btn-primary"
              :disabled="!isFormValid || loading"
            >
              <span v-if="loading" class="loading loading-spinner loading-sm"></span>
              {{ isEditing ? 'Update Schedule' : 'Create Schedule' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch, onMounted } from 'vue'
import CronBuilder from './CronBuilder.vue'
import api from '@/api'

export default {
  name: 'ScheduleEditor',
  components: {
    CronBuilder
  },
  props: {
    editSchedule: {
      type: Object,
      default: null
    }
  },
  emits: ['save', 'cancel'],
  setup(props, { emit }) {
    const loading = ref(false)
    const cronValid = ref(false)
    const newDirectory = ref('')
    const errors = ref({})
    const jellyfinLibraries = ref([])
    const loadingLibraries = ref(false)
    
    // Default schedule structure
    const defaultSchedule = {
      name: '',
      cron: '0 2 * * *',
      timezone: 'UTC',
      enabled: true,
      processing_options: {
        audio_badges: true,
        resolution_badges: true,
        review_badges: true,
        awards_badges: false,
        force_refresh: false,
        target_directories: ['movies', 'tv']
      }
    }
    
    const schedule = ref({ ...defaultSchedule })
    
    // Check if editing existing schedule
    const isEditing = computed(() => !!props.editSchedule)
    
    // Form validation
    const isFormValid = computed(() => {
      return schedule.value.name.trim() && 
             schedule.value.cron.trim() && 
             cronValid.value &&
             (schedule.value.processing_options.audio_badges ||
              schedule.value.processing_options.resolution_badges ||
              schedule.value.processing_options.review_badges ||
              schedule.value.processing_options.awards_badges)
    })
    
    // Watch for editSchedule prop changes
    watch(() => props.editSchedule, (newSchedule) => {
      if (newSchedule) {
        schedule.value = { ...newSchedule }
      } else {
        schedule.value = { ...defaultSchedule }
      }
      errors.value = {}
    }, { immediate: true })
    
    const addDirectory = () => {
      const dir = newDirectory.value.trim()
      if (dir && !schedule.value.processing_options.target_directories.includes(dir)) {
        schedule.value.processing_options.target_directories.push(dir)
        newDirectory.value = ''
      }
    }
    
    const removeDirectory = (index) => {
      schedule.value.processing_options.target_directories.splice(index, 1)
    }
    
    const validateForm = () => {
      errors.value = {}
      
      if (!schedule.value.name.trim()) {
        errors.value.name = 'Schedule name is required'
      }
      
      if (!schedule.value.cron.trim()) {
        errors.value.cron = 'Cron expression is required'
      }
      
      if (!cronValid.value) {
        errors.value.cron = 'Invalid cron expression'
      }
      
      if (!schedule.value.processing_options.audio_badges &&
          !schedule.value.processing_options.resolution_badges &&
          !schedule.value.processing_options.review_badges &&
          !schedule.value.processing_options.awards_badges) {
        errors.value.badges = 'At least one badge type must be selected'
      }
      
      return Object.keys(errors.value).length === 0
    }
    
    const saveSchedule = async () => {
      if (!validateForm()) {
        return
      }
      
      loading.value = true
      
      try {
        const scheduleData = { ...schedule.value }
        
        if (isEditing.value) {
          await api.schedules.updateSchedule(scheduleData.id, scheduleData)
        } else {
          await api.schedules.createSchedule(scheduleData)
        }
        
        emit('save', scheduleData)
      } catch (error) {
        console.error('Error saving schedule:', error)
        // Handle error - maybe show a toast notification
      } finally {
        loading.value = false
      }
    }
    
    // Jellyfin library management
    const fetchJellyfinLibraries = async () => {
      loadingLibraries.value = true
      try {
        const response = await api.schedules.getJellyfinLibraries()
        jellyfinLibraries.value = response.data.libraries || []
      } catch (error) {
        console.error('Error fetching Jellyfin libraries:', error)
        jellyfinLibraries.value = []
      } finally {
        loadingLibraries.value = false
      }
    }
    
    const refreshJellyfinLibraries = () => {
      fetchJellyfinLibraries()
    }
    
    const isLibrarySelected = (library) => {
      return schedule.value.processing_options.target_directories.includes(library.name)
    }
    
    const toggleLibrary = (library, isChecked) => {
      const directories = schedule.value.processing_options.target_directories
      const libraryName = library.name
      
      if (isChecked && !directories.includes(libraryName)) {
        directories.push(libraryName)
      } else if (!isChecked && directories.includes(libraryName)) {
        const index = directories.indexOf(libraryName)
        directories.splice(index, 1)
      }
    }
    
    const getDirectoryBadgeClass = (directory) => {
      // Check if this directory matches a Jellyfin library
      const isJellyfinLibrary = jellyfinLibraries.value.some(lib => lib.name === directory)
      return isJellyfinLibrary ? 'badge-primary' : 'badge-secondary'
    }
    
    // Load Jellyfin libraries on component mount
    onMounted(() => {
      fetchJellyfinLibraries()
    })
    
    return {
      schedule,
      loading,
      cronValid,
      newDirectory,
      errors,
      isEditing,
      isFormValid,
      addDirectory,
      removeDirectory,
      saveSchedule,
      jellyfinLibraries,
      loadingLibraries,
      refreshJellyfinLibraries,
      isLibrarySelected,
      toggleLibrary,
      getDirectoryBadgeClass
    }
  }
}
</script>
