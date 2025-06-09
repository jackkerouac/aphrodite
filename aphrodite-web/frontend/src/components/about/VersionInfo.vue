<template>
  <div>
    <!-- Current Version -->
    <div class="flex justify-between items-center p-4 bg-base-200 rounded-lg">
      <div>
        <div class="font-semibold">Current Version</div>
        <div class="text-lg">v{{ version }}</div>
      </div>
      <button 
        class="btn btn-outline btn-sm"
        @click="$emit('check-updates')"
        :disabled="checkingUpdates"
        title="Check for latest version"
      >
        <svg v-if="checkingUpdates" class="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
        </svg>
        {{ checkingUpdates ? 'Checking...' : 'Check Updates' }}
      </button>
    </div>
    
    <!-- Update notifications -->
    <!-- Update available notification -->
    <div v-if="updateInfo && updateInfo.update_available" class="alert alert-info mt-4">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span>Update available: v{{ updateInfo.latest_version }}</span>
      <div>
        <a :href="updateInfo.release_notes_url" target="_blank" class="btn btn-sm btn-primary">
          View Release Notes
        </a>
      </div>
    </div>
    
    <!-- No update available notification -->
    <div v-if="updateInfo && !updateInfo.update_available" class="alert alert-success mt-4">
      <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" class="stroke-current shrink-0 w-6 h-6">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
      </svg>
      <span>{{ updateInfo.message || 'You are running the latest version!' }}</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'VersionInfo',
  props: {
    version: {
      type: String,
      default: 'Unknown'
    },
    updateInfo: {
      type: Object,
      default: null
    },
    checkingUpdates: {
      type: Boolean,
      default: false
    }
  },
  emits: ['check-updates']
}
</script>
