<template>
  <div class="schedule-history">
    <div class="card bg-base-100 shadow-lg">
      <div class="card-body">
        <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
          <h2 class="card-title">Job Execution History</h2>
          <button 
            @click="refreshHistory"
            class="btn btn-primary btn-sm"
            :disabled="loading"
          >
            <span v-if="loading" class="loading loading-spinner loading-sm"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>
        
        <!-- Filters -->
        <div class="flex flex-col md:flex-row gap-4 mb-6">
          <div class="form-control w-full md:w-auto">
            <select v-model="statusFilter" class="select select-bordered select-sm">
              <option value="">All Status</option>
              <option value="success">Success</option>
              <option value="failed">Failed</option>
              <option value="running">Running</option>
            </select>
          </div>
          
          <div class="form-control w-full md:w-auto">
            <select v-model="scheduleFilter" class="select select-bordered select-sm">
              <option value="">All Schedules</option>
              <option v-for="schedule in schedules" :key="schedule.id" :value="schedule.id">
                {{ schedule.name }}
              </option>
            </select>
          </div>
          
          <div class="form-control w-full md:w-auto">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="Search jobs..."
              class="input input-bordered input-sm"
            />
          </div>
        </div>
        
        <!-- History Table -->
        <div v-if="filteredHistory.length > 0" class="overflow-x-auto">
          <table class="table table-zebra">
            <thead>
              <tr>
                <th>Schedule</th>
                <th>Status</th>
                <th>Started</th>
                <th>Duration</th>
                <th>Details</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="job in paginatedHistory" :key="job.id">
                <td>
                  <div class="font-medium">{{ getScheduleName(job.schedule_id) }}</div>
                  <div class="text-sm opacity-70">{{ job.schedule_id }}</div>
                </td>
                <td>
                  <div class="badge" :class="getStatusClass(job.status)">
                    {{ job.status.toUpperCase() }}
                  </div>
                </td>
                <td>
                  <div class="text-sm">
                    {{ formatDateTime(job.started_at) }}
                  </div>
                </td>
                <td>
                  <div class="text-sm">
                    {{ formatDuration(job.duration) }}
                  </div>
                </td>
                <td>
                  <div class="text-sm max-w-xs truncate" :title="job.message">
                    {{ job.message || 'No details' }}
                  </div>
                </td>
                <td>
                  <div class="flex gap-1">
                    <button 
                      @click="viewJobDetails(job)"
                      class="btn btn-ghost btn-xs"
                      title="View Details"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button 
                      v-if="job.status === 'failed'"
                      @click="retryJob(job)"
                      class="btn btn-ghost btn-xs"
                      title="Retry Job"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="!loading" class="text-center py-12">
          <svg xmlns="http://www.w3.org/2000/svg" class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
          </svg>
          <h3 class="mt-4 text-lg font-medium">No job history found</h3>
          <p class="mt-2 text-sm opacity-70">
            {{ filteredHistory.length === 0 && jobHistory.length > 0 ? 'No jobs match your current filters.' : 'Jobs will appear here after schedules are executed.' }}
          </p>
        </div>
        
        <!-- Loading State -->
        <div v-if="loading" class="text-center py-12">
          <span class="loading loading-spinner loading-lg"></span>
          <p class="mt-4">Loading job history...</p>
        </div>
        
        <!-- Pagination -->
        <div v-if="filteredHistory.length > itemsPerPage" class="flex justify-center mt-6">
          <div class="btn-group">
            <button 
              @click="currentPage--"
              :disabled="currentPage === 1"
              class="btn btn-sm"
            >
              «
            </button>
            <button 
              v-for="page in visiblePages" 
              :key="page"
              @click="currentPage = page"
              class="btn btn-sm"
              :class="{ 'btn-active': currentPage === page }"
            >
              {{ page }}
            </button>
            <button 
              @click="currentPage++"
              :disabled="currentPage === totalPages"
              class="btn btn-sm"
            >
              »
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Job Details Modal -->
    <div v-if="selectedJob" class="modal modal-open">
      <div class="modal-box max-w-2xl">
        <h3 class="font-bold text-lg mb-4">Job Details</h3>
        
        <div class="grid grid-cols-2 gap-4 mb-4">
          <div>
            <div class="text-sm font-medium opacity-70">Schedule</div>
            <div>{{ getScheduleName(selectedJob.schedule_id) }}</div>
          </div>
          <div>
            <div class="text-sm font-medium opacity-70">Status</div>
            <div class="badge" :class="getStatusClass(selectedJob.status)">
              {{ selectedJob.status.toUpperCase() }}
            </div>
          </div>
          <div>
            <div class="text-sm font-medium opacity-70">Started</div>
            <div>{{ formatDateTime(selectedJob.started_at) }}</div>
          </div>
          <div>
            <div class="text-sm font-medium opacity-70">Duration</div>
            <div>{{ formatDuration(selectedJob.duration) }}</div>
          </div>
        </div>
        
        <div v-if="selectedJob.message" class="mb-4">
          <div class="text-sm font-medium opacity-70 mb-2">Message</div>
          <div class="bg-base-200 p-3 rounded text-sm font-mono whitespace-pre-wrap">
            {{ selectedJob.message }}
          </div>
        </div>
        
        <div v-if="selectedJob.error" class="mb-4">
          <div class="text-sm font-medium opacity-70 mb-2">Error Details</div>
          <div class="bg-error bg-opacity-10 p-3 rounded text-sm font-mono whitespace-pre-wrap">
            {{ selectedJob.error }}
          </div>
        </div>
        
        <div v-if="selectedJob.workflow_id" class="mb-4">
          <div class="text-sm font-medium opacity-70 mb-2">Workflow ID</div>
          <div class="font-mono text-sm">
            {{ selectedJob.workflow_id }}
          </div>
        </div>
        
        <div v-if="selectedJob.result_data" class="mb-4">
          <div class="text-sm font-medium opacity-70 mb-2">Processing Results</div>
          <div class="bg-base-200 p-3 rounded text-sm font-mono whitespace-pre-wrap max-h-48 overflow-y-auto">
            {{ formatResultData(selectedJob.result_data) }}
          </div>
        </div>
        
        <div class="modal-action">
          <button @click="selectedJob = null" class="btn btn-primary">Close</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import api from '@/api'

export default {
  name: 'ScheduleHistory',
  setup() {
    const loading = ref(false)
    const jobHistory = ref([])
    const schedules = ref([])
    const selectedJob = ref(null)
    
    // Filters
    const statusFilter = ref('')
    const scheduleFilter = ref('')
    const searchQuery = ref('')
    
    // Pagination
    const currentPage = ref(1)
    const itemsPerPage = ref(25)
    
    // Computed properties
    const filteredHistory = computed(() => {
      // Ensure jobHistory.value is an array
      if (!Array.isArray(jobHistory.value)) {
        console.warn('Job history is not an array:', jobHistory.value)
        return []
      }
      
      let filtered = [...jobHistory.value]
      
      if (statusFilter.value) {
        filtered = filtered.filter(job => job.status === statusFilter.value)
      }
      
      if (scheduleFilter.value) {
        filtered = filtered.filter(job => job.schedule_id === scheduleFilter.value)
      }
      
      if (searchQuery.value) {
        const query = searchQuery.value.toLowerCase()
        filtered = filtered.filter(job => 
          getScheduleName(job.schedule_id).toLowerCase().includes(query) ||
          (job.message && job.message.toLowerCase().includes(query)) ||
          job.status.toLowerCase().includes(query)
        )
      }
      
      return filtered.sort((a, b) => new Date(b.started_at) - new Date(a.started_at))
    })
    
    const totalPages = computed(() => {
      return Math.ceil(filteredHistory.value.length / itemsPerPage.value)
    })
    
    const paginatedHistory = computed(() => {
      const start = (currentPage.value - 1) * itemsPerPage.value
      const end = start + itemsPerPage.value
      return filteredHistory.value.slice(start, end)
    })
    
    const visiblePages = computed(() => {
      if (totalPages.value <= 1) return []
      
      const delta = 2
      const range = []
      const rangeWithDots = []
      
      for (let i = Math.max(2, currentPage.value - delta);
           i <= Math.min(totalPages.value - 1, currentPage.value + delta);
           i++) {
        range.push(i)
      }
      
      if (currentPage.value - delta > 2) {
        rangeWithDots.push(1, '...')
      } else {
        rangeWithDots.push(1)
      }
      
      rangeWithDots.push(...range)
      
      if (currentPage.value + delta < totalPages.value - 1) {
        rangeWithDots.push('...', totalPages.value)
      } else if (totalPages.value > 1) {
        rangeWithDots.push(totalPages.value)
      }
      
      return rangeWithDots.filter((page, index, array) => 
        index === 0 || page !== array[index - 1]
      )
    })
    
    // Methods
    const getScheduleName = (scheduleId) => {
      const schedule = schedules.value.find(s => s.id === scheduleId)
      return schedule ? schedule.name : scheduleId
    }
    
    const getStatusClass = (status) => {
      switch (status) {
        case 'success':
          return 'badge-success'
        case 'failed':
          return 'badge-error'
        case 'running':
          return 'badge-warning'
        default:
          return 'badge-ghost'
      }
    }
    
    const formatDateTime = (dateString) => {
      const date = new Date(dateString)
      return date.toLocaleString()
    }
    
    const formatDuration = (duration) => {
      if (!duration) return 'N/A'
      
      const durationNum = typeof duration === 'string' ? parseFloat(duration) : duration
      if (isNaN(durationNum)) return 'N/A'
      
      if (durationNum < 60) {
        return `${Math.round(durationNum)}s`
      } else if (durationNum < 3600) {
        return `${Math.round(durationNum / 60)}m ${Math.round(durationNum % 60)}s`
      } else {
        const hours = Math.floor(durationNum / 3600)
        const minutes = Math.floor((durationNum % 3600) / 60)
        return `${hours}h ${minutes}m`
      }
    }
    
    const formatResultData = (resultData) => {
      if (!resultData) return 'No result data'
      
      try {
        if (typeof resultData === 'string') {
          const parsed = JSON.parse(resultData)
          return JSON.stringify(parsed, null, 2)
        } else {
          return JSON.stringify(resultData, null, 2)
        }
      } catch (e) {
        return resultData.toString()
      }
    }
    
    const refreshHistory = async () => {
      loading.value = true
      try {
        const [historyResponse, schedulesResponse] = await Promise.all([
          api.schedules.getJobHistory(),
          api.schedules.getSchedules()
        ])
        
        // Process job history data to map database fields to frontend expectations
        let rawHistory = []
        if (historyResponse.data && historyResponse.data.history) {
          rawHistory = historyResponse.data.history
        } else if (Array.isArray(historyResponse.data)) {
          rawHistory = historyResponse.data
        } else {
          rawHistory = []
        }
        
        // Map database fields to frontend expected fields
        jobHistory.value = rawHistory.map(job => ({
          id: job.id,
          schedule_id: job.schedule_id,
          status: job.status,
          started_at: job.started_at,
          duration: job.duration_seconds || job.duration,  // Map duration_seconds → duration
          message: job.message,
          error: job.error_details || job.error,  // Map error_details → error
          // Additional fields available but not displayed in UI
          completed_at: job.completed_at,
          workflow_id: job.workflow_id,
          result_data: job.result_data,
          job_id: job.job_id
        }))
        
        // Process schedules data
        let rawSchedules = []
        if (schedulesResponse.data && schedulesResponse.data.schedules) {
          rawSchedules = schedulesResponse.data.schedules
        } else if (Array.isArray(schedulesResponse.data)) {
          rawSchedules = schedulesResponse.data
        } else {
          rawSchedules = []
        }
        schedules.value = rawSchedules
        
        console.log('Job history loaded:', jobHistory.value.length, 'records')
        console.log('Schedules loaded:', schedules.value.length, 'schedules')
        if (jobHistory.value.length > 0) {
          console.log('Sample job record:', jobHistory.value[0])
        }
      } catch (error) {
        console.error('Error fetching job history:', error)
        // Set defaults on error
        jobHistory.value = []
        schedules.value = []
      } finally {
        loading.value = false
      }
    }
    
    const viewJobDetails = (job) => {
      selectedJob.value = job
    }
    
    const retryJob = async (job) => {
      try {
        await api.schedules.runSchedule(job.schedule_id)
        // Refresh history after retry
        await refreshHistory()
      } catch (error) {
        console.error('Error retrying job:', error)
      }
    }
    
    // Watch for filter changes to reset pagination
    watch([statusFilter, scheduleFilter, searchQuery], () => {
      currentPage.value = 1
    })
    
    // Load data on mount
    onMounted(() => {
      refreshHistory()
    })
    
    return {
      loading,
      jobHistory,
      schedules,
      selectedJob,
      statusFilter,
      scheduleFilter,
      searchQuery,
      currentPage,
      itemsPerPage,
      filteredHistory,
      totalPages,
      paginatedHistory,
      visiblePages,
      getScheduleName,
      getStatusClass,
      formatDateTime,
      formatDuration,
      formatResultData,
      refreshHistory,
      viewJobDetails,
      retryJob
    }
  }
}
</script>
