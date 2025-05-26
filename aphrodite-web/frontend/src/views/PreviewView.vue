<template>
  <div class="preview">
    <h1 class="text-2xl font-bold mb-4">Job History</h1>
    
    <!-- Loading indicator -->
    <div v-if="loading" class="flex justify-center my-8">
      <div class="loading loading-spinner loading-lg"></div>
    </div>
    
    <!-- Error message -->
    <div v-else-if="error" class="alert alert-error shadow-lg mb-4">
      <div>
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current flex-shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ error }}</span>
      </div>
    </div>
    
    <!-- Job history table -->
    <div v-else-if="jobs.length > 0" class="overflow-x-auto">
      <table class="table w-full">
        <thead>
          <tr>
            <th>ID</th>
            <th>Type</th>
            <th>Status</th>
            <th>Start Time</th>
            <th>End Time</th>
            <th>Duration</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="job in jobs" :key="job.id" :class="{ 'bg-success bg-opacity-10': job.status === 'Success', 'bg-error bg-opacity-10': job.status === 'Failed' }">
            <td class="font-mono text-xs">{{ job.id.substring(0, 8) }}</td>
            <td>
              <span class="badge badge-sm" :class="getJobTypeBadgeClass(job.type)">{{ formatJobType(job.type) }}</span>
            </td>
            <td>
              <span class="badge" :class="getStatusBadgeClass(job.status)">{{ job.status }}</span>
            </td>
            <td>{{ formatDateTime(job.start_time) }}</td>
            <td>{{ job.end_time ? formatDateTime(job.end_time) : '-' }}</td>
            <td>{{ calculateDuration(job.start_time, job.end_time) }}</td>
            <td>
              <div class="flex space-x-2">
                <button class="btn btn-xs btn-info" @click="viewJobDetails(job.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                </button>
                <button class="btn btn-xs btn-warning" @click="rerunJob(job.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
                <button class="btn btn-xs btn-error" @click="confirmDeleteJob(job.id)">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <!-- Pagination -->
      <div class="flex justify-center mt-4">
        <div class="btn-group">
          <button 
            class="btn" 
            :class="{ 'btn-disabled': page === 1 }"
            @click="changePage(page - 1)"
          >
            «
          </button>
          <button class="btn">Page {{ page }} of {{ totalPages }}</button>
          <button 
            class="btn" 
            :class="{ 'btn-disabled': page === totalPages }"
            @click="changePage(page + 1)"
          >
            »
          </button>
        </div>
      </div>
    </div>
    
    <!-- No jobs message -->
    <div v-else class="alert alert-info shadow-lg">
      <div>
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current flex-shrink-0 w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>No jobs found. Try running a process first.</span>
      </div>
    </div>
    
    <!-- Job details modal -->
    <div class="modal" :class="{ 'modal-open': selectedJob !== null }">
      <div class="modal-box w-11/12 max-w-5xl relative">
        <!-- Close button in the corner -->
        <button class="btn btn-sm btn-circle absolute right-2 top-2" @click="closeJobDetails">✕</button>
        
        <h3 class="font-bold text-lg pr-10">Job Details</h3>
        <div v-if="selectedJob" class="py-4 space-y-4">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <p><span class="font-bold">ID:</span> {{ selectedJob.id }}</p>
              <p><span class="font-bold">Type:</span> {{ formatJobType(selectedJob.type) }}</p>
              <p><span class="font-bold">Status:</span> 
                <span class="badge" :class="getStatusBadgeClass(selectedJob.status)">{{ selectedJob.status }}</span>
              </p>
            </div>
            <div>
              <p><span class="font-bold">Start Time:</span> {{ formatDateTime(selectedJob.start_time) }}</p>
              <p><span class="font-bold">End Time:</span> {{ selectedJob.end_time ? formatDateTime(selectedJob.end_time) : '-' }}</p>
              <p><span class="font-bold">Duration:</span> {{ calculateDuration(selectedJob.start_time, selectedJob.end_time) }}</p>
            </div>
          </div>
          
          <div v-if="selectedJob.options" class="space-y-2">
            <h4 class="font-semibold">Options</h4>
            <div class="bg-base-200 p-4 rounded-lg">
              <pre class="whitespace-pre-wrap break-words">{{ JSON.stringify(selectedJob.options, null, 2) }}</pre>
            </div>
          </div>
          
          <div v-if="selectedJob.result" class="space-y-2">
            <h4 class="font-semibold">Result</h4>
            <div class="tabs tabs-boxed mb-2">
              <a 
                class="tab" 
                :class="{ 'tab-active': activeTab === 'stdout' }"
                @click="activeTab = 'stdout'"
              >Standard Output</a>
              <a 
                class="tab" 
                :class="{ 'tab-active': activeTab === 'stderr' }"
                @click="activeTab = 'stderr'"
              >Standard Error</a>
            </div>
            <div v-if="activeTab === 'stdout'" class="bg-base-200 p-4 rounded-lg h-64 overflow-auto">
              <pre class="whitespace-pre-wrap break-words">{{ selectedJob.result.stdout || 'No output' }}</pre>
            </div>
            <div v-if="activeTab === 'stderr'" class="bg-base-200 p-4 rounded-lg h-64 overflow-auto">
              <pre class="whitespace-pre-wrap break-words text-error">{{ selectedJob.result.stderr || 'No errors' }}</pre>
            </div>
          </div>
        </div>
        <div class="modal-action">
          <button class="btn btn-primary" @click="closeJobDetails">Close</button>
        </div>
      </div>
      <!-- Click outside to close -->
      <form method="dialog" class="modal-backdrop" @click="closeJobDetails">
        <button>close</button>
      </form>
    </div>
    
    <!-- Delete confirmation modal -->
    <div class="modal" :class="{ 'modal-open': jobToDelete !== null }">
      <div class="modal-box relative">
        <!-- Close button in the corner -->
        <button class="btn btn-sm btn-circle absolute right-2 top-2" @click="jobToDelete = null">✕</button>
        
        <h3 class="font-bold text-lg pr-10">Confirm Deletion</h3>
        <p class="py-4">Are you sure you want to delete this job? This action cannot be undone.</p>
        <div class="modal-action">
          <button class="btn btn-error" @click="deleteJob">Delete</button>
          <button class="btn" @click="jobToDelete = null">Cancel</button>
        </div>
      </div>
      <!-- Click outside to close -->
      <form method="dialog" class="modal-backdrop" @click="jobToDelete = null">
        <button>close</button>
      </form>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import api from '@/api';

export default {
  name: 'PreviewView',
  setup() {
    const loading = ref(true);
    const error = ref(null);
    const jobs = ref([]);
    const page = ref(1);
    const perPage = ref(10);
    const totalJobs = ref(0);
    const totalPages = ref(1);
    const selectedJob = ref(null);
    const jobToDelete = ref(null);
    const activeTab = ref('stdout');
    
    // Fetch jobs from the API
    const fetchJobs = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await api.jobs.getJobs(page.value, perPage.value);
        jobs.value = response.data.jobs;
        totalJobs.value = response.data.total;
        totalPages.value = response.data.total_pages;
      } catch (err) {
        console.error('Error fetching jobs:', err);
        error.value = 'Failed to load job history. Please try again.';
      } finally {
        loading.value = false;
      }
    };
    
    // Change the current page
    const changePage = (newPage) => {
      if (newPage >= 1 && newPage <= totalPages.value) {
        page.value = newPage;
        fetchJobs();
      }
    };
    
    // Format job type for display
    const formatJobType = (type) => {
      if (!type) return 'Unknown';
      
      const typeMap = {
        'check': 'Connection Check',
        'item': 'Single Item',
        'library': 'Library'
      };
      
      return typeMap[type] || type.charAt(0).toUpperCase() + type.slice(1);
    };
    
    // Get badge class for job type
    const getJobTypeBadgeClass = (type) => {
      const classMap = {
        'check': 'badge-info',
        'item': 'badge-primary',
        'library': 'badge-secondary'
      };
      
      return classMap[type] || 'badge-ghost';
    };
    
    // Get badge class for job status
    const getStatusBadgeClass = (status) => {
      const classMap = {
        'Success': 'badge-success',
        'Failed': 'badge-error',
        'Running': 'badge-warning',
        'Queued': 'badge-info',
        'Cancelled': 'badge-ghost'
      };
      
      return classMap[status] || 'badge-ghost';
    };
    
    // Format date and time
    const formatDateTime = (isoString) => {
      if (!isoString) return '-';
      
      try {
        const date = new Date(isoString);
        return date.toLocaleString();
      } catch (err) {
        return isoString;
      }
    };
    
    // Calculate duration between start and end times
    const calculateDuration = (startIso, endIso) => {
      if (!startIso) return '-';
      
      try {
        const start = new Date(startIso);
        const end = endIso ? new Date(endIso) : new Date();
        
        const durationMs = end - start;
        const seconds = Math.floor(durationMs / 1000) % 60;
        const minutes = Math.floor(durationMs / (1000 * 60)) % 60;
        const hours = Math.floor(durationMs / (1000 * 60 * 60));
        
        return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
      } catch (err) {
        return '-';
      }
    };
    
    // View job details
    const viewJobDetails = async (jobId) => {
      loading.value = true;
      
      try {
        const response = await api.jobs.getJob(jobId);
        selectedJob.value = response.data.job;
        activeTab.value = 'stdout'; // Reset tab selection
      } catch (err) {
        console.error('Error fetching job details:', err);
        error.value = 'Failed to load job details. Please try again.';
      } finally {
        loading.value = false;
      }
    };
    
    // Close job details modal
    const closeJobDetails = () => {
      selectedJob.value = null;
    };
    
    // Confirm job deletion
    const confirmDeleteJob = (jobId) => {
      jobToDelete.value = jobId;
    };
    
    // Delete a job
    const deleteJob = async () => {
      if (!jobToDelete.value) return;
      
      try {
        await api.jobs.deleteJob(jobToDelete.value);
        await fetchJobs(); // Refresh the job list
        jobToDelete.value = null; // Close the modal
      } catch (err) {
        console.error('Error deleting job:', err);
        error.value = 'Failed to delete job. Please try again.';
      }
    };
    
    // Rerun a job
    const rerunJob = async (jobId) => {
      try {
        // First, get the job details to get the options
        const response = await api.jobs.getJob(jobId);
        const job = response.data.job;
        
        if (job && job.type) {
          if (job.type === 'item' && job.options) {
            // Rerun single item job
            await api.processSingleItem({
              itemId: job.options.itemId,
              badgeTypes: job.options.badgeTypes || ['audio', 'resolution', 'review'],
              skipUpload: job.options.skipUpload || false
            });
          } else if (job.type === 'library' && job.options) {
            // Rerun library job
            await api.processLibrary({
              libraryIds: [job.options.libraryId],
              badgeTypes: job.options.badgeTypes || ['audio', 'resolution', 'review'],
              limit: job.options.limit,
              skipUpload: job.options.skipUpload || false
            });
          }
          
          // Refresh the job list
          await fetchJobs();
        }
      } catch (err) {
        console.error('Error re-running job:', err);
        error.value = 'Failed to re-run job. Please try again.';
      }
    };
    
    // Load jobs on component mount
    onMounted(() => {
      fetchJobs();
    });
    
    return {
      loading,
      error,
      jobs,
      page,
      perPage,
      totalJobs,
      totalPages,
      selectedJob,
      jobToDelete,
      activeTab,
      fetchJobs,
      changePage,
      formatJobType,
      getJobTypeBadgeClass,
      getStatusBadgeClass,
      formatDateTime,
      calculateDuration,
      viewJobDetails,
      closeJobDetails,
      confirmDeleteJob,
      deleteJob,
      rerunJob
    };
  }
};
</script>
