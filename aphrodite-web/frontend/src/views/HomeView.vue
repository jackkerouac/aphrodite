<template>
  <div class="home">
    <h1 class="text-2xl font-bold mb-2">Aphrodite Dashboard</h1>
    <p class="mb-6 text-gray-600">
      Welcome to Aphrodite - a tool for enhancing Jellyfin media posters with informational badges for audio codecs, resolution, review scores, and award recognition.
    </p>

    <h2 class="text-x1 font-bold mb-2">Latest Updates</h2>

    <div class="collapse collapse-arrow bg-base-100 border border-base-300">
      <input type="radio" name="my-accordion-2" checked="checked" />
      <div class="collapse-title font-semibold">Additions</div>
      <div class="collapse-content text-sm">
        <p><strong>Crunchyroll Anime Awards Integration</strong> - Added support for Crunchyroll Anime Awards!</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Automatic detection for 11 major anime winners (2017-2025)</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Includes Solo Leveling, Demon Slayer, Attack on Titan, Jujutsu Kaisen, My Hero Academia</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; TMDb ID and title-based matching with search variants support</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; High priority in award hierarchy, fully integrated in Settings → Awards</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Multi-color badge support (black, gray, red, yellow) with ribbon styling</p>
        <p>&nbsp;</p>
        <p><strong>Preview Poster System</strong> - Added a new Preview Poster system (<em>work in progress!</em>)</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; You can preview a premade poster (light and/or dark) with rudimentary badges</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; I will eventually have it pick a random poster from Jellyfin to apply the badges to, so you can see real badges and how they would look.</p>
        <p>&nbsp;</p>
        <p><strong>Awards Badge System</strong> - New badge type for award-winning media with ribbon-style badges</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Detects Oscars, Emmys, Golden Globes, BAFTA, Cannes, and 13 more award types</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Multi-source detection using static database + TMDb/OMDB APIs</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; 4 color schemes (black, gray, red, yellow) with web interface configuration</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Flush positioning in bottom-right corner with transparent backgrounds</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; 140+ award-winning titles in database with priority-based selection</p>
      </div>
    </div>
    <div class="collapse collapse-arrow bg-base-100 border border-base-300">
      <input type="radio" name="my-accordion-2" />
      <div class="collapse-title font-semibold">Fixes</div>
      <div class="collapse-content text-sm">
        <p><strong>fix(frontend): badge position settings not persisting on reload</strong></p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Fix shallow merge issue preventing badge positions from loading correctly</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Add loading spinner to Settings page with progress indicators</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Remove unused deepMerge functions causing ESLint errors</p>
        <p>&nbsp;&nbsp;&nbsp;&middot; Badge positions now properly persist from YAML configuration files</p>
      </div>
    </div>
    <div class="collapse collapse-arrow bg-base-100 border border-base-300">
      <input type="radio" name="my-accordion-2" />
      <div class="collapse-title font-semibold">Updates</div>
      <div class="collapse-content text-sm">
        <p>&nbsp;&nbsp;&nbsp;&middot; Updated the API layer to use dynamic URLs</p>
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
