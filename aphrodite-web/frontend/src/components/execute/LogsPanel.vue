<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title">Application Logs</h2>
      <p class="mb-4">View, filter, and manage Aphrodite application logs.</p>
      
      <!-- Controls -->
      <div class="flex flex-wrap gap-4 mb-4">
        <!-- Level Filter -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Log Level</span>
          </label>
          <select v-model="selectedLevel" class="select select-bordered select-sm w-40" @change="fetchLogs">
            <option value="">All Levels</option>
            <option v-for="level in availableLevels" :key="level" :value="level">{{ level }}</option>
          </select>
        </div>
        
        <!-- Search -->
        <div class="form-control flex-1 min-w-48">
          <label class="label">
            <span class="label-text">Search Messages</span>
          </label>
          <div class="input-group">
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="Search log messages..." 
              class="input input-bordered input-sm flex-1"
              @keyup.enter="fetchLogs"
            />
            <button class="btn btn-sm btn-primary" @click="fetchLogs">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </button>
          </div>
        </div>
        
        <!-- Actions -->
        <div class="form-control">
          <label class="label">
            <span class="label-text">Actions</span>
          </label>
          <div class="btn-group">
            <button class="btn btn-sm btn-primary" @click="fetchLogs" :disabled="isLoading">
              <span v-if="isLoading" class="loading loading-spinner loading-xs mr-1"></span>
              Refresh
            </button>
            <button class="btn btn-sm btn-secondary" @click="copyLogs" :disabled="!logs.length">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Copy
            </button>
            <button class="btn btn-sm btn-warning" @click="clearLogs" :disabled="!logs.length">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Clear
            </button>
          </div>
        </div>
      </div>
      
      <!-- File Info -->
      <div v-if="fileInfo" class="alert alert-info mb-4">
        <div class="flex-1">
          <div class="flex justify-between items-center">
            <span class="text-sm">
              <strong>{{ fileInfo.total_lines }}</strong> total lines
              <span v-if="logs.length !== fileInfo.total_lines">
                (showing <strong>{{ logs.length }}</strong> filtered)
              </span>
              • {{ formatFileSize(fileInfo.file_size) }}
              • Last modified: {{ fileInfo.file_modified }}
            </span>
          </div>
        </div>
      </div>
      
      <!-- Loading State -->
      <div v-if="isLoading" class="flex justify-center py-8">
        <span class="loading loading-spinner loading-lg"></span>
      </div>
      
      <!-- Empty State -->
      <div v-else-if="!logs.length && !error" class="text-center py-8">
        <div class="text-lg font-medium mb-2">No logs found</div>
        <p class="text-base-content/70">
          <span v-if="selectedLevel || searchQuery">
            Try adjusting your filters or search query.
          </span>
          <span v-else>
            The log file is empty or doesn't exist yet.
          </span>
        </p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <span>{{ error }}</span>
      </div>
      
      <!-- Logs Display -->
      <div v-else class="bg-base-200 rounded-lg p-4 max-h-96 overflow-auto font-mono text-sm">
        <div 
          v-for="log in logs" 
          :key="log.line_number" 
          class="flex py-1 hover:bg-base-300 rounded px-2 -mx-2"
          :class="getLogLevelClass(log.level)"
        >
          <span class="text-xs text-base-content/50 w-16 flex-shrink-0 mr-3">
            {{ log.line_number }}
          </span>
          <span class="text-xs text-base-content/70 w-40 flex-shrink-0 mr-3">
            {{ log.timestamp }}
          </span>
          <span class="text-xs font-bold w-20 flex-shrink-0 mr-3" :class="getLevelBadgeClass(log.level)">
            {{ log.level }}
          </span>
          <span class="flex-1 break-words">
            {{ log.message }}
          </span>
        </div>
      </div>
      
      <!-- Success/Error Messages -->
      <div v-if="successMessage" class="alert alert-success mt-4">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ successMessage }}</span>
      </div>
      
      <!-- Clear Confirmation Modal -->
      <div v-if="showClearModal" class="modal modal-open">
        <div class="modal-box">
          <h3 class="font-bold text-lg">Clear Logs</h3>
          <p class="py-4">Are you sure you want to clear all logs? This action cannot be undone.</p>
          <div class="modal-action">
            <button class="btn btn-primary" @click="confirmClearLogs">Clear All Logs</button>
            <button class="btn" @click="showClearModal = false">Cancel</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import logsApi from '@/api/logs';

export default {
  name: 'LogsPanel',
  setup() {
    const isLoading = ref(false);
    const logs = ref([]);
    const availableLevels = ref([]);
    const selectedLevel = ref('');
    const searchQuery = ref('');
    const error = ref('');
    const successMessage = ref('');
    const fileInfo = ref(null);
    const showClearModal = ref(false);
    
    // Fetch logs from the API
    const fetchLogs = async () => {
      isLoading.value = true;
      error.value = '';
      
      try {
        const params = {};
        if (selectedLevel.value) params.level = selectedLevel.value;
        if (searchQuery.value) params.search = searchQuery.value;
        params.limit = 1000; // Last 1000 lines
        
        const response = await logsApi.getLogs(params);
        
        if (response.data.success) {
          logs.value = response.data.logs;
          fileInfo.value = {
            total_lines: response.data.total_lines,
            filtered_lines: response.data.filtered_lines,
            file_size: response.data.file_size,
            file_modified: response.data.file_modified
          };
        } else {
          error.value = response.data.message || 'Failed to load logs';
        }
      } catch (err) {
        console.error('Error fetching logs:', err);
        error.value = err.response?.data?.message || 'Error loading logs';
      } finally {
        isLoading.value = false;
      }
    };
    
    // Fetch available log levels
    const fetchLogLevels = async () => {
      try {
        const response = await logsApi.getLogLevels();
        if (response.data.success) {
          availableLevels.value = response.data.levels;
        }
      } catch (err) {
        console.error('Error fetching log levels:', err);
      }
    };
    
    // Copy logs to clipboard
    const copyLogs = async () => {
      if (!logs.value.length) return;
      
      try {
        const logText = logs.value.map(log => 
          `${log.timestamp} - ${log.level} - ${log.message}`
        ).join('\n');
        
        await navigator.clipboard.writeText(logText);
        
        successMessage.value = 'Logs copied to clipboard!';
        setTimeout(() => {
          successMessage.value = '';
        }, 3000);
      } catch (err) {
        console.error('Error copying logs:', err);
        error.value = 'Failed to copy logs to clipboard';
      }
    };
    
    // Clear logs
    const clearLogs = () => {
      showClearModal.value = true;
    };
    
    // Confirm clear logs
    const confirmClearLogs = async () => {
      showClearModal.value = false;
      isLoading.value = true;
      
      try {
        const response = await logsApi.clearLogs();
        
        if (response.data.success) {
          logs.value = [];
          fileInfo.value = null;
          successMessage.value = 'Logs cleared successfully!';
          setTimeout(() => {
            successMessage.value = '';
          }, 3000);
        } else {
          error.value = response.data.message || 'Failed to clear logs';
        }
      } catch (err) {
        console.error('Error clearing logs:', err);
        error.value = err.response?.data?.message || 'Error clearing logs';
      } finally {
        isLoading.value = false;
      }
    };
    
    // Get CSS class for log level
    const getLogLevelClass = (level) => {
      switch (level?.toLowerCase()) {
        case 'error':
        case 'critical':
          return 'bg-error/10';
        case 'warning':
          return 'bg-warning/10';
        case 'info':
          return 'bg-info/10';
        default:
          return '';
      }
    };
    
    // Get badge class for log level
    const getLevelBadgeClass = (level) => {
      switch (level?.toLowerCase()) {
        case 'error':
        case 'critical':
          return 'text-error';
        case 'warning':
          return 'text-warning';
        case 'info':
          return 'text-info';
        case 'debug':
          return 'text-accent';
        default:
          return 'text-base-content/70';
      }
    };
    
    // Format file size
    const formatFileSize = (bytes) => {
      if (!bytes) return '0 B';
      const k = 1024;
      const sizes = ['B', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      return (bytes / Math.pow(k, i)).toFixed(i > 0 ? 1 : 0) + ' ' + sizes[i];
    };
    
    // Initialize
    onMounted(() => {
      fetchLogLevels();
      fetchLogs();
    });
    
    return {
      isLoading,
      logs,
      availableLevels,
      selectedLevel,
      searchQuery,
      error,
      successMessage,
      fileInfo,
      showClearModal,
      fetchLogs,
      copyLogs,
      clearLogs,
      confirmClearLogs,
      getLogLevelClass,
      getLevelBadgeClass,
      formatFileSize
    };
  }
};
</script>
