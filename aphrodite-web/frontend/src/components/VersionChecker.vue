<template>
  <div class="version-checker">
    <!-- Loading state -->
    <div v-if="isLoading || !currentVersion" class="text-sm opacity-70">
      <span v-if="currentVersion">v{{ currentVersion }}</span>
      <span v-else>Loading...</span>
      <span class="loading loading-spinner loading-xs ml-1"></span>
    </div>
    
    <!-- Update available state -->
    <div v-else-if="updateAvailable" class="cursor-pointer" @click="showUpdateModal = true">
      <div class="flex items-center gap-2">
        <span class="text-sm opacity-70">v{{ currentVersion }}</span>
        <div class="badge badge-warning badge-xs">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Update
        </div>
      </div>
      <div class="text-xs opacity-50 mt-1">
        v{{ latestVersion }} available
      </div>
    </div>
    
    <!-- Error state (offline/failed) -->
    <div v-else-if="hasError" class="text-sm opacity-70" :title="errorMessage">
      v{{ currentVersion }} <span class="text-xs opacity-50">(offline)</span>
    </div>

    <!-- Normal version display (default) -->
    <div v-else class="text-sm opacity-70">
      v{{ currentVersion }}
    </div>

    <!-- Update Details Modal -->
    <div v-if="showUpdateModal" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 inline mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          Aphrodite v{{ latestVersion }} Available
        </h3>
        
        <div class="space-y-4">
          <div class="alert alert-info">
            <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path>
            </svg>
            <div>
              <div class="font-bold">You're currently running v{{ currentVersion }}</div>
              <div class="text-sm">A new version (v{{ latestVersion }}) is now available!</div>
            </div>
          </div>

          <!-- Release Notes -->
          <div v-if="releaseNotes" class="bg-base-200 rounded-lg p-4">
            <h4 class="font-semibold mb-2">What's New:</h4>
            <div class="prose prose-sm max-w-none">
              <div v-html="formattedReleaseNotes" class="text-sm"></div>
            </div>
          </div>

          <!-- Published Date -->
          <div v-if="publishedAt" class="text-sm opacity-70">
            Released: {{ formatDate(publishedAt) }}
          </div>
        </div>

        <div class="modal-action">
          <button class="btn btn-primary" @click="openGitHubRelease">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
            View on GitHub
          </button>
          <button class="btn btn-ghost" @click="remindLater">
            Remind me later
          </button>
          <button class="btn btn-ghost" @click="skipVersion">
            Skip this version
          </button>
        </div>
      </div>
      <div class="modal-backdrop" @click="showUpdateModal = false"></div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'VersionChecker',
  data() {
    return {
      currentVersion: null,  // Will be fetched from API
      latestVersion: null,
      updateAvailable: false,
      isLoading: false,
      hasError: false,
      errorMessage: '',
      releaseNotes: '',
      releaseUrl: '',
      publishedAt: '',
      showUpdateModal: false,
      checkSuccessful: false
    };
  },
  computed: {
    formattedReleaseNotes() {
      if (!this.releaseNotes) return '';
      
      // Simple markdown-like formatting for release notes
      return this.releaseNotes
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code class="bg-base-300 px-1 rounded">$1</code>');
    }
  },
  mounted() {
    this.checkForUpdates();
  },
  methods: {
    async checkForUpdates(force = false) {
      // Check if we should skip this check
      if (!force && this.shouldSkipCheck()) {
        return;
      }

      this.isLoading = true;
      this.hasError = false;
      this.errorMessage = '';

      try {
        console.log('VersionChecker: Making API request to /api/version/check');
        const cacheBuster = new Date().getTime();
        const response = await axios.get(`/api/version/check${force ? '?force=true' : ''}${force ? '&' : '?'}_cb=${cacheBuster}`);
        console.log('VersionChecker: API response:', response.data);
        
        if (response.data.success) {
          const data = response.data.data;
          
          this.currentVersion = data.current_version;
          this.latestVersion = data.latest_version;
          this.updateAvailable = data.update_available;
          this.releaseNotes = data.release_notes;
          this.releaseUrl = data.release_url;
          this.publishedAt = data.published_at;
          this.checkSuccessful = data.check_successful;
          
          if (!data.check_successful) {
            this.hasError = true;
            this.errorMessage = data.error || 'Unknown error';
          }

          // Store last check time
          localStorage.setItem('aphrodite_last_version_check', new Date().toISOString());
          
          // Store the check result
          localStorage.setItem('aphrodite_version_data', JSON.stringify(data));
        } else {
          this.hasError = true;
          this.errorMessage = response.data.error || 'Failed to check for updates';
        }
      } catch (error) {
        console.warn('VersionChecker: Failed to check for updates:', error);
        this.hasError = true;
        this.errorMessage = 'Network error';
        
        // Try to load from localStorage as fallback
        this.loadFromLocalStorage();
      } finally {
        this.isLoading = false;
      }
    },
    
    shouldSkipCheck() {
      // Check if we've checked recently (within 24 hours)
      const lastCheck = localStorage.getItem('aphrodite_last_version_check');
      if (lastCheck) {
        const lastCheckTime = new Date(lastCheck);
        const now = new Date();
        const hoursDiff = (now - lastCheckTime) / (1000 * 60 * 60);
        
        if (hoursDiff < 24) {
          // Load cached data
          this.loadFromLocalStorage();
          return true;
        }
      }
      
      return false;
    },
    
    loadFromLocalStorage() {
      try {
        const cachedData = localStorage.getItem('aphrodite_version_data');
        if (cachedData) {
          const data = JSON.parse(cachedData);
          this.currentVersion = data.current_version;
          this.latestVersion = data.latest_version;
          this.updateAvailable = data.update_available && !this.isVersionSkipped(data.latest_version);
          this.releaseNotes = data.release_notes;
          this.releaseUrl = data.release_url;
          this.publishedAt = data.published_at;
          this.checkSuccessful = data.check_successful;
        }
      } catch (error) {
        console.warn('Failed to load cached version data:', error);
      }
    },
    
    isVersionSkipped(version) {
      const skippedVersions = JSON.parse(localStorage.getItem('aphrodite_skipped_versions') || '[]');
      return skippedVersions.includes(version);
    },
    
    skipVersion() {
      if (this.latestVersion) {
        const skippedVersions = JSON.parse(localStorage.getItem('aphrodite_skipped_versions') || '[]');
        if (!skippedVersions.includes(this.latestVersion)) {
          skippedVersions.push(this.latestVersion);
          localStorage.setItem('aphrodite_skipped_versions', JSON.stringify(skippedVersions));
        }
        this.updateAvailable = false;
      }
      this.showUpdateModal = false;
    },
    
    remindLater() {
      // Just close the modal - update will show again after cache expires
      this.showUpdateModal = false;
    },
    
    openGitHubRelease() {
      if (this.releaseUrl) {
        window.open(this.releaseUrl, '_blank', 'noopener,noreferrer');
      }
      this.showUpdateModal = false;
    },
    
    formatDate(dateString) {
      try {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        });
      } catch (error) {
        return dateString;
      }
    }
  }
};
</script>

<style scoped>
.version-checker {
  /* Add any component-specific styles here */
}

/* Ensure modal displays above sidebar */
.modal {
  z-index: 9999;
}
</style>
