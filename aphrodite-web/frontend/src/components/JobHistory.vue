<template>
  <div class="job-history">
    <!-- Template content omitted for brevity -->
  </div>
</template>

<script>
import api from '@/api';

export default {
  name: 'JobHistory',
  data() {
    return {
      jobs: [],
      loading: true,
      currentPage: 1,
      totalPages: 1,
      totalItems: 0,
      itemsPerPage: 10,
      jobTypeFilter: '',
      
      selectedJob: null,
      jobItems: [],
      itemsPage: 1,
      itemsTotalPages: 1,
      totalItemsForJob: 0,
      
      selectedComparison: null,
      jobToDelete: null,
      
      // Polling
      pollingInterval: null
    };
  },
  
  mounted() {
    this.fetchJobs(1);
    // Set up polling every 5 seconds
    this.startPolling();
  },
  
  beforeUnmount() {
    this.stopPolling();
  },
  
  methods: {
    startPolling() {
      this.pollingInterval = setInterval(() => {
        // Only refresh if there are running jobs
        if (this.jobs.some(job => job.status === 'Running')) {
          this.fetchJobs(this.currentPage, false);
        }
      }, 5000);
    },
    
    stopPolling() {
      if (this.pollingInterval) {
        clearInterval(this.pollingInterval);
        this.pollingInterval = null;
      }
    },
    
    async fetchJobs(page, showLoading = true) {
      if (showLoading) {
        this.loading = true;
      }
      
      try {
        const response = await api.jobs.getJobs(page, this.itemsPerPage, this.jobTypeFilter);
        
        if (response.data.success) {
          this.jobs = response.data.jobs;
          this.totalItems = response.data.total;
          this.currentPage = response.data.page;
          this.totalPages = response.data.total_pages;
        } else {
          console.error('Failed to fetch jobs:', response.data.message);
        }
      } catch (error) {
        console.error('Error fetching jobs:', error);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchJobItems(jobId, page = 1) {
      try {
        const response = await api.jobs.getJobItems(jobId, page, this.itemsPerPage);
        
        if (response.data.success) {
          this.jobItems = response.data.items;
          this.totalItemsForJob = response.data.total;
          this.itemsPage = response.data.page;
          this.itemsTotalPages = response.data.total_pages;
        } else {
          console.error('Failed to fetch job items:', response.data.message);
        }
      } catch (error) {
        console.error('Error fetching job items:', error);
      }
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      try {
        const date = new Date(dateStr);
        return new Intl.DateTimeFormat('en-US', {
          year: 'numeric',
          month: 'short',
          day: '2-digit',
          hour: '2-digit',
          minute: '2-digit',
          second: '2-digit',
          hour12: false
        }).format(date);
      } catch (error) {
        return dateStr;
      }
    },
    
    jobTypeLabel(type) {
      switch (type) {
        case 'item': return 'Single Item';
        case 'library': return 'Library';
        case 'check': return 'Connection Check';
        default: return type;
      }
    },
    
    getJobTitle(job) {
      if (job.type === 'item') {
        return job.options?.title || job.options?.itemId || 'Unknown Item';
      } else if (job.type === 'library') {
        return `${job.options?.libraryName || 'Unknown Library'} (${job.result?.processed_count || 0} items)`;
      } else {
        return 'Jellyfin Connection Check';
      }
    },
    
    async viewJobDetails(job) {
      // If the job is not selected yet, fetch its items
      if (!this.selectedJob || this.selectedJob.id !== job.id) {
        this.selectedJob = job;
        
        if (job.type === 'library') {
          await this.fetchJobItems(job.id, 1);
        }
      } else {
        // If it's already selected, just toggle visibility
        this.selectedJob = null;
      }
    },
    
    closeJobDetails() {
      this.selectedJob = null;
      this.jobItems = [];
      this.itemsPage = 1;
    },
    
    viewFullComparison(item) {
      this.selectedComparison = item;
    },
    
    closeFullComparison() {
      this.selectedComparison = null;
    },
    
    getImagePath(path) {
      return api.jobs.getImagePath(path);
    },
    
    downloadImage(filename) {
      return api.jobs.downloadImage(filename);
    },
    
    getFilenameFromPath(path) {
      if (!path) return '';
      return path.split(/[\\/]/).pop();
    },
    
    confirmDeleteJob(job) {
      this.jobToDelete = job;
    },
    
    cancelDelete() {
      this.jobToDelete = null;
    },
    
    async deleteJob() {
      if (!this.jobToDelete) return;
      
      try {
        const response = await api.jobs.deleteJob(this.jobToDelete.id);
        
        if (response.data.success) {
          // Remove the job from the list
          this.jobs = this.jobs.filter(job => job.id !== this.jobToDelete.id);
          
          // If it was the selected job, close the details modal
          if (this.selectedJob && this.selectedJob.id === this.jobToDelete.id) {
            this.closeJobDetails();
          }
          
          // Close the delete confirmation modal
          this.jobToDelete = null;
          
          // If the job list is now empty and we're not on the first page, go back one page
          if (this.jobs.length === 0 && this.currentPage > 1) {
            this.fetchJobs(this.currentPage - 1);
          }
        } else {
          console.error('Failed to delete job:', response.data.message);
        }
      } catch (error) {
        console.error('Error deleting job:', error);
      }
    },
    
    rerunJob(job) {
      const jobType = job.type;
      
      if (jobType === 'item' && job.options) {
        // Re-run an item job
        api.processSingleItem(job.options)
          .then(() => {
            // Refresh the job list
            this.fetchJobs(1);
            // Close modals
            this.closeJobDetails();
            this.jobToDelete = null;
          })
          .catch(error => {
            console.error('Error re-running item job:', error);
          });
      } else if (jobType === 'library' && job.options) {
        // Re-run a library job
        api.processLibrary(job.options)
          .then(() => {
            // Refresh the job list
            this.fetchJobs(1);
            // Close modals
            this.closeJobDetails();
            this.jobToDelete = null;
          })
          .catch(error => {
            console.error('Error re-running library job:', error);
          });
      }
    }
  }
};
</script>
