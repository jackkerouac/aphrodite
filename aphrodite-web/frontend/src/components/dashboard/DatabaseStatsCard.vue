<template>
  <div class="card bg-base-100 shadow-xl">
    <div class="card-body">
      <h2 class="card-title flex items-center">
        <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
        Poster Statistics
      </h2>
      
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center py-8">
        <span class="loading loading-spinner loading-md"></span>
        <p class="text-gray-500 ml-2">Loading poster statistics...</p>
      </div>
      
      <!-- Error State -->
      <div v-else-if="error" class="alert alert-warning">
        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <span>{{ error }}</span>
      </div>
      
      <!-- No Data State -->
      <div v-else-if="!stats || stats.total_items === 0" class="text-center py-6">
        <div class="flex flex-col items-center">
          <svg class="w-12 h-12 text-gray-400 mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h8c0-2.21-1.79-4-4-4H8c-2.21 0-4-1.79-4-4z" />
          </svg>
          <p class="text-gray-500">No processed items yet</p>
          <p class="text-sm text-gray-400">Start processing some media to see statistics here</p>
        </div>
      </div>
      
      <!-- Statistics Display -->
      <div v-else>
        <!-- Main Stats Grid -->
        <div class="stats stats-vertical lg:stats-horizontal shadow bg-base-200 mb-4">
          <div class="stat">
            <div class="stat-figure text-primary">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            <div class="stat-title">Total Items</div>
            <div class="stat-value text-primary">{{ stats.total_items.toLocaleString() }}</div>
            <div class="stat-desc">Processed media items</div>
          </div>
          
          <div class="stat">
            <div class="stat-figure text-success">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div class="stat-title">Success Rate</div>
            <div class="stat-value text-success">{{ stats.success_rate }}%</div>
            <div class="stat-desc">{{ status_breakdown.success || 0 }} successful</div>
          </div>
          
          <div class="stat">
            <div class="stat-figure text-info">
              <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div class="stat-title">Avg Processing</div>
            <div class="stat-value text-info">{{ formatDuration(stats.performance_metrics.avg_processing_time) }}</div>
            <div class="stat-desc">Per item</div>
          </div>
        </div>
        
        <!-- Recent Activity -->
        <div class="mb-4">
          <h3 class="text-lg font-semibold mb-2">Recent Activity</h3>
          <div class="grid grid-cols-3 gap-2">
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">24 Hours</div>
              <div class="stat-value text-sm">{{ stats.recent_activity.last_24h }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">7 Days</div>
              <div class="stat-value text-sm">{{ stats.recent_activity.last_7d }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">30 Days</div>
              <div class="stat-value text-sm">{{ stats.recent_activity.last_30d }}</div>
            </div>
          </div>
        </div>
        
        <!-- Status Breakdown -->
        <div v-if="Object.keys(status_breakdown).length > 0" class="mb-4">
          <h3 class="text-lg font-semibold mb-2">Processing Status</h3>
          <div class="space-y-2">
            <div v-for="(count, status) in status_breakdown" :key="status" class="flex justify-between items-center">
              <span class="capitalize">{{ formatStatus(status) }}</span>
              <div class="flex items-center">
                <span class="mr-2">{{ count }}</span>
                <div class="w-20 bg-gray-200 rounded-full h-2">
                  <div 
                    class="h-2 rounded-full" 
                    :class="getStatusColor(status)"
                    :style="{ width: (count / stats.total_items * 100) + '%' }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Review Insights -->
        <div v-if="stats.review_insights.items_with_reviews > 0" class="mb-4">
          <h3 class="text-lg font-semibold mb-2">Review Insights</h3>
          <div class="grid grid-cols-2 gap-2">
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">Items with Reviews</div>
              <div class="stat-value text-sm">{{ stats.review_insights.items_with_reviews }}</div>
            </div>
            <div class="stat bg-base-200 rounded-lg">
              <div class="stat-title">Avg Score</div>
              <div class="stat-value text-sm">{{ stats.review_insights.avg_review_score }}/10</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Action Button -->
      <div class="card-actions justify-end mt-4">
        <button class="btn btn-sm btn-outline btn-primary" @click="refreshStats">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Refresh
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import api from '@/api';

export default {
  name: 'DatabaseStatsCard',
  setup() {
    const stats = ref(null);
    const loading = ref(true);
    const error = ref(null);

    // Computed property for status breakdown
    const status_breakdown = computed(() => {
      return stats.value?.status_breakdown || {};
    });

    // Load statistics
    const loadStats = async () => {
      try {
        loading.value = true;
        error.value = null;
        
        console.log('Fetching database statistics...');
        const response = await api.database.getStats();
        console.log('Database stats response:', response.data);
        
        if (response.data.success) {
          stats.value = response.data.stats;
        } else {
          error.value = response.data.message || 'Failed to load database statistics';
        }
      } catch (err) {
        console.error('Error loading database statistics:', err);
        error.value = 'Database tracking not available. This feature requires processed items.';
        stats.value = null;
      } finally {
        loading.value = false;
      }
    };

    // Refresh statistics
    const refreshStats = () => {
      loadStats();
    };

    // Format duration in seconds to human readable
    const formatDuration = (seconds) => {
      if (!seconds || seconds === 0) return '0s';
      
      if (seconds < 60) {
        return `${seconds.toFixed(1)}s`;
      } else if (seconds < 3600) {
        return `${(seconds / 60).toFixed(1)}m`;
      } else {
        return `${(seconds / 3600).toFixed(1)}h`;
      }
    };

    // Format status text
    const formatStatus = (status) => {
      const statusMap = {
        'success': 'Success',
        'failed': 'Failed',
        'partial_success': 'Partial Success',
        'processing': 'Processing',
        'needs_reprocessing': 'Needs Reprocessing'
      };
      return statusMap[status] || status;
    };

    // Get color class for status
    const getStatusColor = (status) => {
      const colorMap = {
        'success': 'bg-success',
        'failed': 'bg-error',
        'partial_success': 'bg-warning',
        'processing': 'bg-info',
        'needs_reprocessing': 'bg-warning'
      };
      return colorMap[status] || 'bg-gray-400';
    };

    // Load statistics on component mount
    onMounted(() => {
      loadStats();
    });

    return {
      stats,
      loading,
      error,
      status_breakdown,
      refreshStats,
      formatDuration,
      formatStatus,
      getStatusColor
    };
  }
};
</script>
