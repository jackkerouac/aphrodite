<template>
  <div class="schedule-manager">
    <div class="card bg-base-100 shadow-lg">
      <div class="card-body">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <div>
            <h2 class="card-title">Schedule Manager</h2>
            <p class="text-sm opacity-70 mt-1">Manage automated processing schedules</p>
          </div>
          <div class="flex gap-2">
            <button 
              @click="refreshSchedules"
              class="btn btn-ghost btn-sm"
              :disabled="loading"
            >
              <span v-if="loading" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
            <button 
              @click="showCreateForm"
              class="btn btn-primary btn-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              New Schedule
            </button>
          </div>
        </div>
        
        <!-- Scheduler Status -->
        <div class="alert mb-6" :class="schedulerStatusClass">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-5 w-5" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
          </svg>
          <div>
            <div class="font-medium">Scheduler Status: {{ getSchedulerStatusText() }}</div>
            <div class="text-sm opacity-70">
              {{ schedulerStatus.job_count || 0 }} running jobs, 
              {{ getActiveSchedulesCount() }} active schedules
            </div>
          </div>
        </div>
        
        <!-- Schedules List -->
        <div v-if="schedules.length > 0" class="space-y-4">
          <div 
            v-for="schedule in schedules" 
            :key="schedule.id"
            class="card bg-base-200"
          >
            <div class="card-body p-4">
              <div class="flex flex-col md:flex-row justify-between items-start gap-4">
                <div class="flex-1">
                  <div class="flex items-center gap-2 mb-2">
                    <h3 class="font-medium text-lg">{{ schedule.name }}</h3>
                    <div class="badge" :class="schedule.enabled ? 'badge-success' : 'badge-ghost'">
                      {{ schedule.enabled ? 'Enabled' : 'Disabled' }}
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 text-sm">
                    <div>
                      <div class="font-medium opacity-70">Schedule</div>
                      <div class="font-mono">{{ schedule.cron }}</div>
                      <div class="text-xs opacity-60">{{ getCronDescription(schedule.cron) }}</div>
                    </div>
                    
                    <div>
                      <div class="font-medium opacity-70">Target Libraries</div>
                      <div v-if="schedule.processing_options.target_directories?.length > 0" class="flex flex-wrap gap-1 mt-1">
                        <div 
                          v-for="dir in schedule.processing_options.target_directories" 
                          :key="dir"
                          class="badge badge-xs badge-primary"
                        >
                          {{ dir }}
                        </div>
                      </div>
                      <div v-else class="text-xs opacity-60">No libraries selected</div>
                    </div>
                    
                    <div>
                      <div class="font-medium opacity-70">Badge Types</div>
                      <div class="flex flex-wrap gap-1 mt-1">
                        <div v-if="schedule.processing_options.audio_badges" class="badge badge-xs badge-secondary">Audio</div>
                        <div v-if="schedule.processing_options.resolution_badges" class="badge badge-xs badge-accent">Resolution</div>
                        <div v-if="schedule.processing_options.review_badges" class="badge badge-xs badge-info">Review</div>
                        <div v-if="schedule.processing_options.awards_badges" class="badge badge-xs badge-warning">Awards</div>
                      </div>
                    </div>
                  </div>
                  
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm mt-4">
                    <div>
                      <div class="font-medium opacity-70">Next Run</div>
                      <div>{{ formatDateTime(schedule.next_run) }}</div>
                    </div>
                    
                    <div>
                      <div class="font-medium opacity-70">Last Run</div>
                      <div>{{ schedule.last_run ? formatDateTime(schedule.last_run) : 'Never' }}</div>
                    </div>
                  </div>
                </div>
                
                <!-- Actions -->
                <div class="flex flex-col gap-2">
                  <div class="dropdown dropdown-end">
                    <div tabindex="0" role="button" class="btn btn-ghost btn-sm">
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v.01M12 12v.01M12 19v.01M12 6a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2zm0 7a1 1 0 110-2 1 1 0 010 2z" />
                      </svg>
                    </div>
                    <ul tabindex="0" class="dropdown-content z-[1] menu p-2 shadow bg-base-100 rounded-box w-52">
                      <li>
                        <a @click="runSchedule(schedule)">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-4a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          Run Now
                        </a>
                      </li>
                      <li>
                        <a @click="editSchedule(schedule)">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                          </svg>
                          Edit
                        </a>
                      </li>
                      <li>
                        <a @click="schedule.enabled ? pauseSchedule(schedule) : resumeSchedule(schedule)">
                          <svg v-if="schedule.enabled" xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 9v6m4-6v6m7-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-4a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          {{ schedule.enabled ? 'Pause' : 'Resume' }}
                        </a>
                      </li>
                      <li>
                        <a @click="deleteSchedule(schedule)" class="text-error">
                          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                          </svg>
                          Delete
                        </a>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="!loading" class="text-center py-12">
          <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="mt-4 text-lg font-medium">No schedules found</h3>
          <p class="mt-2 text-sm opacity-70">Get started by creating your first automated schedule.</p>
          <button 
            @click="showCreateForm"
            class="btn btn-primary mt-4"
          >
            Create Schedule
          </button>
        </div>
        
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <span class="loading loading-spinner loading-lg"></span>
          <p class="mt-4">Loading schedules...</p>
        </div>
      </div>
    </div>
    
    <!-- Confirmation Modal -->
    <ConfirmationModal
      :is-open="confirmModal.isOpen"
      :title="confirmModal.title"
      :message="confirmModal.message"
      :confirm-text="confirmModal.confirmText"
      :variant="confirmModal.variant"
      :loading="confirmModal.loading"
      @confirm="handleConfirmAction"
      @cancel="hideConfirmModal"
      @close="hideConfirmModal"
    />
    
    <!-- Notification Modal -->
    <NotificationModal
      :is-open="notificationModal.isOpen"
      :title="notificationModal.title"
      :message="notificationModal.message"
      :variant="notificationModal.variant"
      @close="hideNotification"
    />
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import api from '@/api'
import ConfirmationModal from '@/components/ConfirmationModal.vue'
import NotificationModal from '@/components/NotificationModal.vue'

export default {
  name: 'ScheduleManager',
  components: {
    ConfirmationModal,
    NotificationModal
  },
  emits: ['create-schedule', 'edit-schedule'],
  setup(_, { emit }) {
    const loading = ref(false)
    const schedules = ref([])
    const schedulerStatus = ref({})
    
    // Confirmation modal state
    const confirmModal = ref({
      isOpen: false,
      title: '',
      message: '',
      confirmText: 'Confirm',
      variant: 'primary',
      loading: false,
      action: null
    })
    
    // Notification modal state
    const notificationModal = ref({
      isOpen: false,
      title: '',
      message: '',
      variant: 'success'
    })
    
    // Computed properties
    const schedulerStatusClass = computed(() => {
      // Use the 'running' field from the API response
      if (schedulerStatus.value.running === true) {
        return 'alert-success'
      } else if (schedulerStatus.value.running === false) {
        return 'alert-error'
      } else {
        return 'alert-info'
      }
    })
    
    // Methods
    const formatDateTime = (dateString) => {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    const getCronDescription = (cron) => {
      // Simple cron description - could be enhanced with a proper cron parser
      const commonPatterns = {
        '0 * * * *': 'Every hour',
        '0 0 * * *': 'Daily at midnight',
        '0 2 * * *': 'Daily at 2:00 AM',
        '0 0 * * 0': 'Weekly on Sunday',
        '0 0 1 * *': 'Monthly on 1st',
        '0 */6 * * *': 'Every 6 hours',
        '0 2 * * 1-5': 'Weekdays at 2:00 AM'
      }
      
      return commonPatterns[cron] || 'Custom schedule'
    }
    
    const getSchedulerStatusText = () => {
      if (schedulerStatus.value.running === true) {
        return 'Running'
      } else if (schedulerStatus.value.running === false) {
        return 'Stopped'
      } else {
        return 'Unknown'
      }
    }
    
    const getActiveSchedulesCount = () => {
      // Count enabled schedules
      return schedules.value.filter(schedule => schedule.enabled).length
    }
    
    // Modal helper methods
    const showConfirmModal = (options) => {
      confirmModal.value = {
        isOpen: true,
        title: options.title || 'Confirm Action',
        message: options.message,
        confirmText: options.confirmText || 'Confirm',
        variant: options.variant || 'primary',
        loading: false,
        action: options.action
      }
    }
    
    const hideConfirmModal = () => {
      confirmModal.value.isOpen = false
      confirmModal.value.loading = false
      confirmModal.value.action = null
    }
    
    const showNotification = (options) => {
      notificationModal.value = {
        isOpen: true,
        title: options.title,
        message: options.message,
        variant: options.variant || 'success'
      }
    }
    
    const hideNotification = () => {
      notificationModal.value.isOpen = false
    }
    
    const handleConfirmAction = async () => {
      if (confirmModal.value.action) {
        confirmModal.value.loading = true
        try {
          await confirmModal.value.action()
        } catch (error) {
          console.error('Error executing confirmed action:', error)
        } finally {
          hideConfirmModal()
        }
      }
    }
    
    const refreshSchedules = async () => {
      loading.value = true
      try {
        const [schedulesResponse, statusResponse] = await Promise.all([
          api.schedules.getSchedules(),
          api.schedules.getSchedulerStatus()
        ])
        
        console.log('DEBUG: Schedules response:', schedulesResponse.data)
        console.log('DEBUG: Status response:', statusResponse.data)
        
        // Extract schedules array from the response
        schedules.value = schedulesResponse.data.schedules || []
        schedulerStatus.value = statusResponse.data.status || {}
      } catch (error) {
        console.error('Error fetching schedules:', error)
        schedules.value = []
        schedulerStatus.value = {}
      } finally {
        loading.value = false
      }
    }
    
    const showCreateForm = () => {
      emit('create-schedule')
    }
    
    const editSchedule = (schedule) => {
      emit('edit-schedule', schedule)
    }
    
    const runSchedule = async (schedule) => {
      try {
        await api.schedules.runSchedule(schedule.id)
        // Refresh schedules to update status
        await refreshSchedules()
        
        // Show success notification
        showNotification({
          title: 'Schedule Started',
          message: `Successfully started "${schedule.name}".`,
          variant: 'success'
        })
      } catch (error) {
        console.error('Error running schedule:', error)
        showNotification({
          title: 'Error',
          message: `Failed to start schedule: ${error.message}`,
          variant: 'error'
        })
      }
    }
    
    const pauseSchedule = async (schedule) => {
      try {
        await api.schedules.pauseSchedule(schedule.id)
        await refreshSchedules()
      } catch (error) {
        console.error('Error pausing schedule:', error)
      }
    }
    
    const resumeSchedule = async (schedule) => {
      try {
        await api.schedules.resumeSchedule(schedule.id)
        await refreshSchedules()
      } catch (error) {
        console.error('Error resuming schedule:', error)
      }
    }
    
    const deleteSchedule = async (schedule) => {
      showConfirmModal({
        title: 'Delete Schedule',
        message: `Are you sure you want to delete the schedule "${schedule.name}"? This action cannot be undone.`,
        confirmText: 'Delete',
        variant: 'error',
        action: async () => {
          try {
            await api.schedules.deleteSchedule(schedule.id)
            await refreshSchedules()
            
            // Show success notification
            showNotification({
              title: 'Schedule Deleted',
              message: `Successfully deleted "${schedule.name}".`,
              variant: 'success'
            })
          } catch (error) {
            console.error('Error deleting schedule:', error)
            showNotification({
              title: 'Error',
              message: `Failed to delete schedule: ${error.message}`,
              variant: 'error'
            })
            throw error
          }
        }
      })
    }
    
    // Load data on mount
    onMounted(() => {
      refreshSchedules()
    })
    
    return {
      loading,
      schedules,
      schedulerStatus,
      schedulerStatusClass,
      formatDateTime,
      getCronDescription,
      getSchedulerStatusText,
      getActiveSchedulesCount,
      refreshSchedules,
      showCreateForm,
      editSchedule,
      runSchedule,
      pauseSchedule,
      resumeSchedule,
      deleteSchedule,
      // Modal state and methods
      confirmModal,
      hideConfirmModal,
      handleConfirmAction,
      notificationModal,
      showNotification,
      hideNotification
    }
  }
}
</script>
