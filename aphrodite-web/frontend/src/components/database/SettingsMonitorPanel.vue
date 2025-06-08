<template>
  <div class="space-y-6">
    <!-- Header -->
    <div>
      <h2 class="text-2xl font-bold">Settings Monitor</h2>
      <p class="text-base-content/70">Track badge settings changes and manage reprocessing</p>
    </div>

    <!-- Settings Status -->
    <div class="card bg-base-100 shadow">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h3 class="card-title">Settings Status</h3>
          <button 
            @click="checkSettings" 
            :disabled="loading"
            class="btn btn-sm btn-primary"
          >
            <span v-if="loading" class="loading loading-spinner loading-sm"></span>
            <span v-else>Check Settings</span>
          </button>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <h4 class="font-semibold mb-3">Settings Hash</h4>
            <div class="space-y-2">
              <div class="flex justify-between items-center">
                <span class="text-sm">Current:</span>
                <code class="text-xs bg-base-200 px-2 py-1 rounded">{{ currentHash }}</code>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-sm">Last Check:</span>
                <span class="text-xs">{{ formatDate(lastCheck) }}</span>
              </div>
            </div>
          </div>

          <div>
            <h4 class="font-semibold mb-3">Change Detection</h4>
            <div class="space-y-2">
              <div class="flex items-center gap-2">
                <div class="badge" :class="settingsChanged ? 'badge-warning' : 'badge-success'">
                  {{ settingsChanged ? 'Changes Detected' : 'No Changes' }}
                </div>
              </div>
              <div v-if="settingsChanged" class="text-sm text-warning">
                {{ itemsAffected }} items may need reprocessing
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex justify-center py-8">
      <span class="loading loading-spinner loading-lg"></span>
    </div>

    <!-- Settings Changed Warning -->
    <div v-if="settingsChanged && itemsAffected > 0" class="alert alert-warning">
      <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.464 0L4.35 16.5c-.77.833.192 2.5 1.732 2.5z" />
      </svg>
      <div>
        <div class="font-semibold">Settings Change Detected</div>
        <div class="text-sm">{{ itemsAffected }} items may need reprocessing due to badge settings changes.</div>
      </div>
      <button 
        @click="markForReprocessing" 
        :disabled="marking"
        class="btn btn-sm btn-warning"
      >
        <span v-if="marking" class="loading loading-spinner loading-sm"></span>
        <span v-else>Mark for Reprocessing</span>
      </button>
    </div>

    <!-- Current Badge Settings -->
    <div class="card bg-base-100 shadow">
      <div class="card-body">
        <h3 class="card-title">Current Badge Settings</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-4">
          <div class="border rounded-lg p-3">
            <h4 class="font-semibold text-sm mb-2">🔊 Audio Badges</h4>
            <div class="space-y-1">
              <div class="flex items-center justify-between text-xs">
                <span>Enabled:</span>
                <div class="badge badge-success badge-xs">Yes</div>
              </div>
              <div class="text-xs opacity-70">DTS-HD, Dolby Atmos</div>
            </div>
          </div>

          <div class="border rounded-lg p-3">
            <h4 class="font-semibold text-sm mb-2">📺 Resolution</h4>
            <div class="space-y-1">
              <div class="flex items-center justify-between text-xs">
                <span>Enabled:</span>
                <div class="badge badge-success badge-xs">Yes</div>
              </div>
              <div class="text-xs opacity-70">4K, 1080p, HDR</div>
            </div>
          </div>

          <div class="border rounded-lg p-3">
            <h4 class="font-semibold text-sm mb-2">⭐ Reviews</h4>
            <div class="space-y-1">
              <div class="flex items-center justify-between text-xs">
                <span>Enabled:</span>
                <div class="badge badge-success badge-xs">Yes</div>
              </div>
              <div class="text-xs opacity-70">IMDB, Rotten Tomatoes</div>
            </div>
          </div>

          <div class="border rounded-lg p-3">
            <h4 class="font-semibold text-sm mb-2">🏆 Awards</h4>
            <div class="space-y-1">
              <div class="flex items-center justify-between text-xs">
                <span>Enabled:</span>
                <div class="badge badge-warning badge-xs">Partial</div>
              </div>
              <div class="text-xs opacity-70">Oscar, Emmy</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Settings Change History -->
    <div class="card bg-base-100 shadow">
      <div class="card-body">
        <h3 class="card-title">Recent Settings Changes</h3>
        <div class="space-y-3 mt-4">
          <div v-for="change in settingsHistory" :key="change.id" class="border-l-4 border-primary pl-4">
            <div class="flex justify-between items-start">
              <div>
                <div class="font-semibold text-sm">{{ change.description }}</div>
                <div class="text-xs opacity-70">{{ formatDate(change.timestamp) }}</div>
              </div>
              <div class="badge badge-outline badge-xs">{{ change.type }}</div>
            </div>
          </div>
          
          <div v-if="settingsHistory.length === 0" class="text-center text-sm opacity-50 py-4">
            No recent settings changes detected
          </div>
        </div>
      </div>
    </div>

    <!-- Auto-Detection Settings -->
    <div class="card bg-base-100 shadow">
      <div class="card-body">
        <h3 class="card-title">Auto-Detection Settings</h3>
        <div class="form-control mt-4">
          <label class="label cursor-pointer">
            <span class="label-text">Automatically mark items for reprocessing when settings change</span>
            <input 
              v-model="autoReprocess" 
              @change="updateAutoReprocess"
              type="checkbox" 
              class="checkbox checkbox-primary" 
            />
          </label>
          <div class="label">
            <span class="label-text-alt opacity-70">
              When enabled, items will be automatically marked for reprocessing when badge settings are modified.
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'SettingsMonitorPanel',
  data() {
    return {
      loading: false,
      marking: false,
      error: null,
      currentHash: 'a1b2c3d4e5f6',
      lastCheck: new Date().toISOString(),
      settingsChanged: true,
      itemsAffected: 23,
      autoReprocess: false,
      settingsHistory: [
        {
          id: 1,
          description: 'Review badge threshold changed from 7.0 to 7.5',
          timestamp: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
          type: 'Review'
        },
        {
          id: 2,
          description: 'Audio badge settings updated',
          timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
          type: 'Audio'
        }
      ]
    }
  },
  mounted() {
    this.checkSettings()
  },
  methods: {
    async checkSettings() {
      this.loading = true
      this.error = null
      
      try {
        await new Promise(resolve => setTimeout(resolve, 1000))
        this.lastCheck = new Date().toISOString()
      } catch (error) {
        this.error = `Error checking settings: ${error.message}`
      } finally {
        this.loading = false
      }
    },
    
    async markForReprocessing() {
      this.marking = true
      
      try {
        await new Promise(resolve => setTimeout(resolve, 2000))
        this.settingsChanged = false
        this.itemsAffected = 0
        console.log('Items marked for reprocessing successfully')
      } catch (error) {
        this.error = `Error marking items for reprocessing: ${error.message}`
      } finally {
        this.marking = false
      }
    },
    
    async updateAutoReprocess() {
      try {
        await new Promise(resolve => setTimeout(resolve, 500))
        console.log('Auto-reprocess setting updated:', this.autoReprocess)
      } catch (error) {
        console.error('Failed to update auto-reprocess setting:', error)
        this.autoReprocess = !this.autoReprocess
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '-'
      const date = new Date(dateString)
      const now = new Date()
      const diffMs = now - date
      const diffHours = Math.floor(diffMs / (1000 * 60 * 60))
      const diffDays = Math.floor(diffHours / 24)
      
      if (diffDays > 7) {
        return date.toLocaleDateString()
      } else if (diffDays > 0) {
        return `${diffDays}d ago`
      } else if (diffHours > 0) {
        return `${diffHours}h ago`
      } else {
        return 'Just now'
      }
    }
  }
}
</script>

<style scoped>
.border-l-4 {
  border-left-width: 4px;
}
</style>
