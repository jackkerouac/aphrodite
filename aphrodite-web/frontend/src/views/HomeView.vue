<template>
  <div class="home">
    <h1 class="text-2xl font-bold mb-2">Aphrodite Dashboard</h1>
    <p class="mb-6 text-gray-600">
      Welcome to Aphrodite - a tool for enhancing Jellyfin media posters with informational badges for audio codecs, resolution, review scores, and award recognition.
    </p>

    <h2 class="text-x1 font-bold mb-2">Latest Updates</h2>

    <!-- Dynamic changes from YAML file -->
    <div v-if="changes.length > 0">
      <div 
        v-for="(change, index) in changes" 
        :key="index"
        class="collapse collapse-arrow bg-base-100 border border-base-300 mb-2"
      >
        <input type="radio" name="my-accordion-2" :checked="index === 0" />
        <div class="collapse-title font-semibold">
          <span class="capitalize">{{ change.category }}</span> - {{ change.title }}
          <span class="text-xs text-gray-500 ml-2">({{ change.date }})</span>
        </div>
        <div class="collapse-content text-sm">
          <p><strong>{{ change.title }}</strong> - {{ change.description }}</p>
          <div v-if="change.details && change.details.length > 0">
            <p v-for="(detail, detailIndex) in change.details" :key="detailIndex">
              &nbsp;&nbsp;&nbsp;&middot; {{ detail }}
            </p>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading state -->
    <div v-else class="text-center py-4">
      <span class="loading loading-spinner loading-md"></span>
      <p class="text-gray-500 mt-2">Loading latest updates...</p>
    </div>

    <p>&nbsp;</p>

    <!-- Active Badge Processing Card -->
    <ActiveBadgeJobs @view-progress="handleViewProgress" />

    <p>&nbsp;</p>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Quick Stats Card -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Job Statistics</h2>
          <div class="stats stats-vertical shadow bg-base-200">
            <div class="stat">
              <div class="stat-title">Total Jobs</div>
              <div class="stat-value">{{ jobStats.total || 0 }}</div>
            </div>
            <div class="stat">
              <div class="stat-title">Success Rate</div>
              <div class="stat-value text-success">{{ jobStats.successRate || '0%' }}</div>
            </div>
          </div>
          <div class="card-actions justify-end mt-2">
            <button class="btn btn-sm btn-primary" @click="goToHistory">View History</button>
          </div>
        </div>
      </div>
      
      <!-- Quick Actions Card -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Quick Actions</h2>
          <div class="space-y-3">
            <button class="btn btn-primary w-full" @click="goToPosterManager()">Poster Manager</button>
            <button class="btn btn-secondary w-full" @click="goToExecute('check')">Check Connections</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Global Progress Modal -->
    <GlobalProgressModal 
      :batch-id="selectedBatchId"
      :is-visible="showProgressModal"
      @close="closeProgressModal"
    />
  </div>
</template>

<script>
import { reactive, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';
import ActiveBadgeJobs from '@/components/dashboard/ActiveBadgeJobs.vue';
import GlobalProgressModal from '@/components/dashboard/GlobalProgressModal.vue';

export default {
  name: 'HomeView',
  components: {
    ActiveBadgeJobs,
    GlobalProgressModal
  },
  setup() {
    const router = useRouter();
    const jobStats = reactive({
      total: 0,
      successRate: '0%'
    });
    const changes = ref([]);
    const showProgressModal = ref(false);
    const selectedBatchId = ref(null);

    // Navigate to Settings page
    const goToSettings = () => {
      router.push('/settings');
    };

    // Navigate to History page (schedules with history tab)
    const goToHistory = () => {
      router.push({
        path: '/schedules',
        query: { tab: 'history' }
      });
    };

    // Navigate to Execute page with tab
    const goToExecute = (tab) => {
      router.push({
        path: '/execute',
        query: { tab: tab }
      });
    };

    // Navigate to Poster Manager page
    const goToPosterManager = () => {
      router.push('/poster-manager');
    };

    // Get job statistics
    const getJobStats = async () => {
      try {
        console.log('Getting job statistics...');
        const response = await api.jobs.getJobs();
        console.log('Job statistics response:', response.data);
        
        // Access the jobs array from the response
        const jobs = response.data.jobs || [];
        
        jobStats.total = jobs.length;
        
        if (jobs.length > 0) {
          const successfulJobs = jobs.filter(job => job.status === 'Success').length;
          jobStats.successRate = `${Math.round((successfulJobs / jobs.length) * 100)}%`;
        }
      } catch (error) {
        console.error('Failed to get job statistics:', error);
      }
    };

    // Get changes from YAML file
    const getChanges = async () => {
      try {
        console.log('Getting changes...');
        const response = await api.changes.getChanges();
        console.log('Changes response:', response.data);
        changes.value = response.data.changes || [];
      } catch (error) {
        console.error('Failed to get changes:', error);
        changes.value = [];
      }
    };

    // Load data on component mount
    onMounted(async () => {
      await getJobStats();
      await getChanges();
    });

    // Handle viewing progress from ActiveBadgeJobs component
    const handleViewProgress = (batchId) => {
      selectedBatchId.value = batchId;
      showProgressModal.value = true;
    };

    // Close progress modal
    const closeProgressModal = () => {
      showProgressModal.value = false;
      selectedBatchId.value = null;
    };

    return {
      jobStats,
      changes,
      showProgressModal,
      selectedBatchId,
      goToSettings,
      goToHistory,
      goToExecute,
      goToPosterManager,
      handleViewProgress,
      closeProgressModal
    };
  }
};
</script>
