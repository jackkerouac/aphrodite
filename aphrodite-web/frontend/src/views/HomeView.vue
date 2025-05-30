<template>
  <div class="home">
    <h1 class="text-2xl font-bold mb-2">Aphrodite Dashboard</h1>
    <p class="mb-6 text-gray-600">
      Welcome to Aphrodite - a tool for enhancing Jellyfin media posters with informational badges for audio codecs, resolution, and review scores.
    </p>

    <h2 class="text-x1 font-bold mb-2">Latest Updates</h2>

    <div class="collapse collapse-arrow bg-base-100 border border-base-300">
      <input type="radio" name="my-accordion-2" checked="checked" />
      <div class="collapse-title font-semibold">Additions</div>
      <div class="collapse-content text-sm">
        <p>&nbsp;&nbsp;&nbsp;&middot; Added aphrodite-overlay metadata tag to successfully processed items for future feature tracking</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Added Restore Original Posters feature, under Execute -> Poster Management</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Added episode_timeout setting (default: 15 seconds)</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Specific timeout handling for individual episodes</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Graceful failure handling with proper error messages</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Added max_episodes_to_analyze setting (default: 50)</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Smart sampling - analyzes first N episodes for large series</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Prevents overwhelming API calls for very long series</p>
      </div>
    </div>
    <div class="collapse collapse-arrow bg-base-100 border border-base-300">
      <input type="radio" name="my-accordion-2" />
      <div class="collapse-title font-semibold">Fixes</div>
      <div class="collapse-content text-sm">
        <p>&nbsp;&nbsp;&nbsp;&middot; Added new favicon (like you care or anyone actually reads this)</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Continue processing even if some episodes fail</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Track and report failed episodes</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Return results based on successfully analyzed episodes</p>
      </div>
    </div>
    <div class="collapse collapse-arrow bg-base-100 border border-base-300">
      <input type="radio" name="my-accordion-2" />
      <div class="collapse-title font-semibold">Updates</div>
      <div class="collapse-content text-sm">
        <p>&nbsp;&nbsp;&nbsp;&middot; Updated the API layer to use dynamic URLs</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Shows episode-by-episode progress</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Indicates which episodes succeed/fail</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Displays final statistics and distributions</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Reduced batch sizes for better responsiveness</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Added delays between API calls</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Better memory management</p>
      </div>
    </div>

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
            <button class="btn btn-sm btn-primary" @click="goToPreview">View History</button>
          </div>
        </div>
      </div>
      
      <!-- Quick Actions Card -->
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Quick Actions</h2>
          <div class="space-y-3">
            <button class="btn btn-primary w-full" @click="goToExecute('item')">Process Single Item</button>
            <button class="btn btn-primary w-full" @click="goToExecute('library')">Process Library</button>
            <button class="btn btn-secondary w-full" @click="goToExecute('check')">Check Connections</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';

export default {
  name: 'HomeView',
  setup() {
    const router = useRouter();
    const jobStats = reactive({
      total: 0,
      successRate: '0%'
    });

    // Navigate to Settings page
    const goToSettings = () => {
      router.push('/settings');
    };

    // Navigate to Preview page
    const goToPreview = () => {
      router.push('/preview');
    };

    // Navigate to Execute page with tab
    const goToExecute = (tab) => {
      router.push({
        path: '/execute',
        query: { tab: tab }
      });
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

    // Load data on component mount
    onMounted(async () => {
      await getJobStats();
    });

    return {
      jobStats,
      goToSettings,
      goToPreview,
      goToExecute
    };
  }
};
</script>
