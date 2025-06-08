<template>
  <div class="home">
    <h1 class="text-2xl font-bold mb-2">Aphrodite Dashboard</h1>
    <p class="mb-6 text-gray-600">
      Welcome to Aphrodite - a tool for enhancing Jellyfin media posters with informational badges for audio codecs, resolution, review scores, and award recognition.
    </p>

    <!-- Active Badge Processing Card -->
    <ActiveBadgeJobs @view-progress="handleViewProgress" />

    <p>&nbsp;</p>

    <!-- Poster Statistics Card -->
    <DatabaseStatsCard />

    <!-- Global Progress Modal -->
    <GlobalProgressModal 
      :batch-id="selectedBatchId"
      :is-visible="showProgressModal"
      @close="closeProgressModal"
    />
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/api';
import ActiveBadgeJobs from '@/components/dashboard/ActiveBadgeJobs.vue';
import GlobalProgressModal from '@/components/dashboard/GlobalProgressModal.vue';
import DatabaseStatsCard from '@/components/dashboard/DatabaseStatsCard.vue';

export default {
  name: 'HomeView',
  components: {
    ActiveBadgeJobs,
    GlobalProgressModal,
    DatabaseStatsCard
  },
  setup() {
    const router = useRouter();
    const changes = ref([]);
    const showProgressModal = ref(false);
    const selectedBatchId = ref(null);

    // Navigate to Settings page
    const goToSettings = () => {
      router.push('/settings');
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
      changes,
      showProgressModal,
      selectedBatchId,
      goToSettings,
      handleViewProgress,
      closeProgressModal
    };
  }
};
</script>
