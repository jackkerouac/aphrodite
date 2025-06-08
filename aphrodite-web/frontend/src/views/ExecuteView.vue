<template>
  <div class="execute">
    <h1 class="text-2xl font-bold mb-4">Maintenance</h1>
    
    <div class="mb-6">
      <p class="mb-4">Use the tools below to check your Jellyfin connection and manage your poster files.</p>
      
      <div class="tabs tabs-boxed mb-6">
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'check' }"
          @click="activeTab = 'check'"
        >
          Connection Check
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'cleanup' }"
          @click="activeTab = 'cleanup'"
        >
          Clean Up and Restore
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'database' }"
          @click="activeTab = 'database'"
        >
          Database Operations
        </a>
      </div>
      
      <!-- Connection Check Form -->
      <div v-if="activeTab === 'check'">
        <ConnectionCheck />
      </div>
      
      <!-- Poster Management Form -->
      <div v-else-if="activeTab === 'cleanup'">
        <CleanupForm @cleanup-submitted="handleProcessSubmitted" />
      </div>
      
      <!-- Database Operations Form -->
      <div v-else-if="activeTab === 'database'">
        <DatabaseOperationsPanel @operation-completed="handleDatabaseOperation" />
      </div>
    </div>
    
    <!-- Results Section -->
    <div v-if="showResults" class="mt-8">
      <div class="card bg-base-100 shadow-xl">
        <div class="card-body">
          <h2 class="card-title">Processing Results</h2>
          
            <div v-if="isLoading" class="flex justify-center py-8">
              <span class="loading loading-spinner loading-lg"></span>
            </div>
            
            <div v-else-if="processResult">
              <div class="alert" :class="processResult.success ? 'alert-success' : 'alert-error'">
                <div>
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0" 
                       :class="processResult.success ? 'stroke-current' : 'stroke-current'" 
                       fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{{ processResult.message }}</span>
                </div>
              </div>
              
              <div v-if="processResult.stdout || processResult.stderr" class="mt-4">
                <div v-if="processResult.stdout">
                  <h3 class="font-bold">Output:</h3>
                  <pre class="bg-base-200 p-2 mt-1 rounded-md overflow-auto">{{ processResult.stdout }}</pre>
                </div>
                
                <div v-if="processResult.stderr" class="mt-3">
                  <h3 class="font-bold">Errors:</h3>
                  <pre class="bg-base-200 p-2 mt-1 rounded-md overflow-auto text-error">{{ processResult.stderr }}</pre>
                </div>
              </div>
              
              <!-- Restore-specific results -->
              <div v-if="processResult.restored_count !== undefined" class="mt-4">
                <div class="stats shadow">
                  <div class="stat">
                    <div class="stat-title">Files Restored</div>
                    <div class="stat-value text-primary">{{ processResult.restored_count }}</div>
                  </div>
                  <div class="stat" v-if="processResult.uploaded_count !== undefined">
                    <div class="stat-title">Uploaded to Jellyfin</div>
                    <div class="stat-value text-success">{{ processResult.uploaded_count }}</div>
                  </div>
                  <div class="stat" v-if="processResult.errors && processResult.errors.length > 0">
                    <div class="stat-title">Errors</div>
                    <div class="stat-value text-error">{{ processResult.errors.length }}</div>
                  </div>
                </div>
                
                <!-- Success message for restore operations -->
                <div v-if="processResult.uploaded_count > 0 && processResult.errors.length === 0" class="alert alert-success mt-4">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <div>
                    <h3 class="font-bold">Restore Complete!</h3>
                    <p class="text-sm mt-1">
                      Original posters have been restored and are now visible in Jellyfin. 
                      All badge modifications have been removed.
                    </p>
                  </div>
                </div>
                
                <!-- Re-upload warning for restore operations (legacy - should not appear anymore) -->
                <div v-if="processResult.requires_reupload" class="alert alert-warning mt-4">
                  <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 flex-shrink-0 stroke-current" fill="none" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                  <div>
                    <h3 class="font-bold">Re-upload Required</h3>
                    <p class="text-sm mt-1">
                      The poster files have been restored on disk, but Jellyfin still shows the old versions. 
                      To complete the restore process, you need to re-run the normal Aphrodite processing 
                      for each item to upload the restored posters back to Jellyfin.
                    </p>
                  </div>
                </div>
                
                <div v-if="processResult.errors && processResult.errors.length > 0" class="mt-4">
                  <h3 class="font-bold">Errors:</h3>
                  <div class="bg-base-200 p-2 mt-1 rounded-md">
                    <ul class="list-disc list-inside text-error">
                      <li v-for="error in processResult.errors" :key="error">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <!-- Cleanup-specific results -->
              <div v-else-if="processResult.cleaned_count !== undefined" class="mt-4">
                <div class="stats shadow">
                  <div class="stat">
                    <div class="stat-title">Files Cleaned</div>
                    <div class="stat-value text-primary">{{ processResult.cleaned_count }}</div>
                  </div>
                  <div class="stat" v-if="processResult.directories_processed">
                    <div class="stat-title">Directories Processed</div>
                    <div class="stat-value">{{ processResult.directories_processed }}</div>
                  </div>
                  <div class="stat" v-if="processResult.errors && processResult.errors.length > 0">
                    <div class="stat-title">Errors</div>
                    <div class="stat-value text-error">{{ processResult.errors.length }}</div>
                  </div>
                </div>
                
                <div v-if="processResult.errors && processResult.errors.length > 0" class="mt-4">
                  <h3 class="font-bold">Errors:</h3>
                  <div class="bg-base-200 p-2 mt-1 rounded-md">
                    <ul class="list-disc list-inside text-error">
                      <li v-for="error in processResult.errors" :key="error">{{ error }}</li>
                    </ul>
                  </div>
                </div>
              </div>
              
              <!-- General results -->
              <div v-else class="mt-4">
                <p v-if="processResult.success" class="font-bold">Processing completed successfully!</p>
                <p v-else class="font-bold">Processing failed with code: {{ processResult.returnCode }}</p>
              </div>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

import ConnectionCheck from '@/components/execute/ConnectionCheck.vue';
import CleanupForm from '@/components/execute/CleanupForm.vue';
import DatabaseOperationsPanel from '@/components/database/DatabaseOperationsPanel.vue';

export default {
  name: 'ExecuteView',
  components: {
    ConnectionCheck,
    CleanupForm,
    DatabaseOperationsPanel
  },
  setup() {
    const route = useRouter().currentRoute.value;
    const activeTab = ref('check');
    const isLoading = ref(false);
    const processResult = ref(null);
    const showResults = ref(false);
    
    // Handle route query parameters
    if (route.query.tab) {
      const validTabs = ['check', 'cleanup', 'database'];
      if (validTabs.includes(route.query.tab)) {
        activeTab.value = route.query.tab;
      }
    }
    
    const handleProcessSubmitted = (result) => {
      processResult.value = result;
      showResults.value = true;
      isLoading.value = false;
    };
    
    const handleDatabaseOperation = (result) => {
      processResult.value = result;
      showResults.value = true;
      isLoading.value = false;
    };
    
    return {
      activeTab,
      isLoading,
      processResult,
      showResults,
      handleProcessSubmitted,
      handleDatabaseOperation
    };
  }
}
</script>
