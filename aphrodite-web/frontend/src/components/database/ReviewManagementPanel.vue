<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold">Review Management</h2>
      <p class="text-base-content/70">Monitor and update review data for processed items</p>
    </div>

    <!-- Controls -->
    <div class="card bg-base-100 shadow">
      <div class="card-body">
        <div class="flex flex-col lg:flex-row justify-between items-start lg:items-center gap-4">
          <div class="form-control">
            <label class="label">
              <span class="label-text">Staleness Threshold</span>
            </label>
            <select 
              v-model="hoursThreshold" 
              @change="loadReviewData"
              class="select select-bordered select-sm"
            >
              <option value="24">24 hours</option>
              <option value="48">48 hours</option>
              <option value="72">72 hours</option>
              <option value="168">1 week</option>
            </select>
          </div>
          
          <button 
            @click="loadReviewData" 
            :disabled="loading"
            class="btn btn-sm btn-primary"
          >
            <span v-if="loading" class="loading loading-spinner loading-sm"></span>
            <span v-else>Refresh</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-12">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Error State -->
    <div v-else-if="error" class="alert alert-error">
      <span>{{ error }}</span>
      <button @click="loadReviewData" class="btn btn-sm">Retry</button>
    </div>

    <!-- Review Management Content -->
    <div v-else class="space-y-6">
      <!-- Summary Stats -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div class="stats-card bg-base-100 p-4 rounded-lg shadow">
          <div class="stat">
            <div class="stat-title">Never Checked</div>
            <div class="stat-value text-warning">{{ mockStats.never_checked }}</div>
            <div class="stat-desc">No review data</div>
          </div>
        </div>
        
        <div class="stats-card bg-base-100 p-4 rounded-lg shadow">
          <div class="stat">
            <div class="stat-title">Very Stale</div>
            <div class="stat-value text-error">{{ mockStats.very_stale }}</div>
            <div class="stat-desc">&gt; {{ hoursThreshold * 7 }}h old</div>
          </div>
        </div>
        
        <div class="stats-card bg-base-100 p-4 rounded-lg shadow">
          <div class="stat">
            <div class="stat-title">Stale</div>
            <div class="stat-value text-warning">{{ mockStats.stale }}</div>
            <div class="stat-desc">&gt; {{ hoursThreshold }}h old</div>
          </div>
        </div>
        
        <div class="stats-card bg-base-100 p-4 rounded-lg shadow">
          <div class="stat">
            <div class="stat-title">Recent</div>
            <div class="stat-value text-success">{{ mockStats.recent }}</div>
            <div class="stat-desc">Up to date</div>
          </div>
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex flex-wrap gap-3" v-if="hasStaleItems">
        <button 
          class="btn btn-warning"
          :disabled="updating"
        >
          <span v-if="updating" class="loading loading-spinner loading-sm"></span>
          <span v-else>Update Stale Reviews</span>
        </button>
        
        <button 
          class="btn btn-info"
          :disabled="updating"
          v-if="mockStats.never_checked > 0"
        >
          Process Never Checked
        </button>
      </div>

      <!-- Information Cards -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <h3 class="card-title text-warning">Items Needing Attention</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span>Never checked for reviews</span>
                <div class="badge badge-warning">{{ mockStats.never_checked }}</div>
              </div>
              <div class="flex justify-between items-center">
                <span>Very stale (&gt; {{ hoursThreshold * 7 }}h)</span>
                <div class="badge badge-error">{{ mockStats.very_stale }}</div>
              </div>
              <div class="flex justify-between items-center">
                <span>Stale (&gt; {{ hoursThreshold }}h)</span>
                <div class="badge badge-warning">{{ mockStats.stale }}</div>
              </div>
            </div>
          </div>
        </div>

        <div class="card bg-base-100 shadow">
          <div class="card-body">
            <h3 class="card-title text-success">Review Status Overview</h3>
            <div class="space-y-3">
              <div class="flex justify-between items-center">
                <span>Items with recent review data</span>
                <div class="badge badge-success">{{ mockStats.recent }}</div>
              </div>
              <div class="flex justify-between items-center">
                <span>Total processed items</span>
                <div class="badge badge-outline">{{ totalItems }}</div>
              </div>
              <div class="flex justify-between items-center">
                <span>Up-to-date percentage</span>
                <div class="badge badge-info">{{ upToDatePercentage }}%</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Review Update Instructions -->
      <div class="card bg-base-100 shadow">
        <div class="card-body">
          <h3 class="card-title">Review Update Process</h3>
          <div class="space-y-4">
            <div class="alert alert-info">
              <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div>
                <div class="font-semibold">How Review Updates Work</div>
                <div class="text-sm mt-1">
                  Review data is cached to improve performance. Items are considered "stale" when their review data 
                  hasn't been updated within the specified threshold. Use the buttons above to refresh review data 
                  for items that need attention.
                </div>
              </div>
            </div>
            
            <div class="steps steps-vertical lg:steps-horizontal">
              <div class="step step-primary">Check staleness</div>
              <div class="step step-primary">Fetch new reviews</div>
              <div class="step step-primary">Update badges</div>
              <div class="step">Complete</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- No Data State -->
    <div v-if="!loading && !error && totalItems === 0" class="text-center py-12">
      <div class="text-base-content/50 mb-4">
        <div class="text-6xl mb-4">⭐</div>
        <h3 class="text-lg font-semibold mb-2">No Review Data Available</h3>
        <p>Process some items with review badges to see review management options here.</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReviewManagementPanel',
  data() {
    return {
      loading: false,
      updating: false,
      error: null,
      hoursThreshold: 24,
      mockStats: {
        never_checked: 12,
        very_stale: 8,
        stale: 15,
        recent: 45
      }
    }
  },
  computed: {
    totalItems() {
      return this.mockStats.never_checked + this.mockStats.very_stale + 
             this.mockStats.stale + this.mockStats.recent
    },
    
    hasStaleItems() {
      return this.mockStats.stale > 0 || this.mockStats.very_stale > 0 || this.mockStats.never_checked > 0
    },
    
    upToDatePercentage() {
      if (this.totalItems === 0) return 100
      return Math.round((this.mockStats.recent / this.totalItems) * 100)
    }
  },
  mounted() {
    this.loadReviewData()
  },
  methods: {
    async loadReviewData() {
      this.loading = true
      this.error = null
      
      try {
        // Simulate API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        
        // In real implementation, this would call the review management API
        // For now, we're using mock data
        
      } catch (error) {
        this.error = `Error loading review data: ${error.message}`
        console.error('Failed to load review data:', error)
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
.stats-card {
  transition: transform 0.2s ease-in-out;
}

.stats-card:hover {
  transform: translateY(-2px);
}
</style>
