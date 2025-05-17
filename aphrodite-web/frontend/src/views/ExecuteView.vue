<template>
  <div class="execute">
    <h1 class="text-2xl font-bold mb-4">Execute</h1>
    
    <div class="mb-6">
      <p class="mb-4">Use the forms below to process Jellyfin items with the Aphrodite script.</p>
      
      <div class="tabs tabs-boxed mb-6">
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'item' }"
          @click="activeTab = 'item'"
        >
          Process Single Item
        </a>
        <a 
          class="tab" 
          :class="{ 'tab-active': activeTab === 'library' }"
          @click="activeTab = 'library'"
        >
          Process Library
        </a>
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
          Clean Up Posters
        </a>
      </div>
      
      <!-- Single Item Processing Form -->
      <div v-if="activeTab === 'item'">
        <ItemForm @process-submitted="handleProcessSubmitted" />
      </div>
      
      <!-- Library Processing Form -->
      <div v-else-if="activeTab === 'library'">
        <WorkflowManager class="mb-6" />
        <LibraryForm @process-submitted="handleProcessSubmitted" />
      </div>
      
      <!-- Connection Check Form -->
      <div v-else-if="activeTab === 'check'">
        <ConnectionCheck />
      </div>
      
      <!-- Cleanup Form -->
      <div v-else-if="activeTab === 'cleanup'">
        <CleanupForm @cleanup-submitted="handleProcessSubmitted" />
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
              
              <div class="mt-4">
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
import ItemForm from '@/components/execute/ItemForm.vue';
import LibraryForm from '@/components/execute/LibraryForm.vue';
import WorkflowManager from '@/components/execute/WorkflowManager.vue';
import ConnectionCheck from '@/components/execute/ConnectionCheck.vue';
import CleanupForm from '@/components/execute/CleanupForm.vue';

export default {
  name: 'ExecuteView',
  components: {
    ItemForm,
    LibraryForm,
    WorkflowManager,
    ConnectionCheck,
    CleanupForm
  },
  setup() {
    const route = useRouter().currentRoute.value;
    const activeTab = ref('item');
    const isLoading = ref(false);
    const processResult = ref(null);
    const showResults = ref(false);
    
    // Handle route query parameters
    if (route.query.tab) {
      const validTabs = ['item', 'library', 'check'];
      if (validTabs.includes(route.query.tab)) {
        activeTab.value = route.query.tab;
      }
    }
    
    const handleProcessSubmitted = (result) => {
      processResult.value = result;
      showResults.value = true;
      isLoading.value = false;
    };
    
    return {
      activeTab,
      isLoading,
      processResult,
      showResults,
      handleProcessSubmitted
    };
  }
}
</script>
