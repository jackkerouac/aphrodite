<template>
  <div class="card bg-base-100 shadow-xl mb-6">
    <div class="card-body">
      <h2 class="card-title">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 7v10c0 2.21 1.79 4 4 4h8c2.21 0 4-1.79 4-4V7c0-2.21-1.79-4-4-4H8c-2.21 0-4 1.79-4 4z" />
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 11l3 3 3-3" />
        </svg>
        Database Migration Status
      </h2>
      
      <div v-if="isChecking" class="flex items-center gap-2">
        <div class="loading loading-spinner loading-sm"></div>
        <span>Checking migration status...</span>
      </div>
      
      <div v-else-if="checkError" class="alert alert-error">
        <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <span>{{ checkError }}</span>
      </div>
      
      <div v-else>
        <div v-if="migrationData && migrationData.databaseVersion > 0" class="alert alert-success">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="font-bold">Settings migrated to SQLite!</h3>
            <div class="text-xs">Your settings are now using the new database format (version {{ migrationData.databaseVersion }}).</div>
          </div>
        </div>
        
        <div v-else-if="migrationData && migrationData.yamlExists" class="alert alert-warning">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <div>
            <h3 class="font-bold">Migration available!</h3>
            <div class="text-xs">Your settings can be migrated to a new database format for better performance.</div>
          </div>
        </div>
        
        <div v-else class="alert alert-info">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div>
            <h3 class="font-bold">New installation</h3>
            <div class="text-xs">This appears to be a new installation using the database format.</div>
          </div>
        </div>
        
        <!-- Migration Details -->
        <div v-if="migrationData" class="mt-4">
          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span class="font-semibold">YAML Files:</span>
              <span :class="migrationData.yamlExists ? 'text-success' : 'text-base-content/60'">
                {{ migrationData.yamlExists ? 'Found' : 'Not found' }}
              </span>
            </div>
            <div>
              <span class="font-semibold">Database:</span>
              <span :class="migrationData.databaseExists ? 'text-success' : 'text-base-content/60'">
                {{ migrationData.databaseExists ? 'Exists' : 'Not created' }}
              </span>
            </div>
            <div>
              <span class="font-semibold">DB Version:</span>
              <span>{{ migrationData.databaseVersion }}</span>
            </div>
            <div>
              <span class="font-semibold">Migration Needed:</span>
              <span :class="migrationData.migrationNeeded ? 'text-warning' : 'text-success'">
                {{ migrationData.migrationNeeded ? 'Yes' : 'No' }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Actions -->
      <div v-if="migrationData && migrationData.migrationNeeded" class="card-actions justify-end mt-4">
        <button @click="startMigration" class="btn btn-primary btn-sm">
          Start Migration
        </button>
      </div>
      
      <div v-else-if="migrationData && migrationData.databaseVersion > 0" class="card-actions justify-end mt-4">
        <button @click="refreshStatus" class="btn btn-ghost btn-sm">
          Refresh Status
        </button>
      </div>
    </div>
    
    <!-- Migration Modal -->
    <MigrationModal 
      :isOpen="showMigrationModal" 
      @close="showMigrationModal = false"
      @migration-complete="handleMigrationComplete"
    />
  </div>
</template>

<script>
import { ref } from 'vue';
import { useMigration } from '@/composables/useMigration';
import MigrationModal from './MigrationModal.vue';

export default {
  name: 'MigrationStatus',
  components: {
    MigrationModal
  },
  setup() {
    const { 
      migrationNeeded, 
      isChecking, 
      checkError, 
      checkMigrationStatus 
    } = useMigration();
    
    const showMigrationModal = ref(false);
    const migrationData = ref(null);
    
    // Get detailed migration data
    const refreshStatus = async () => {
      const result = await checkMigrationStatus();
      migrationData.value = result;
    };
    
    // Load migration data on mount
    refreshStatus();
    
    const startMigration = () => {
      showMigrationModal.value = true;
    };
    
    const handleMigrationComplete = () => {
      showMigrationModal.value = false;
      // Refresh the status after migration
      setTimeout(() => {
        refreshStatus();
      }, 1000);
    };
    
    return {
      migrationNeeded,
      isChecking,
      checkError,
      migrationData,
      showMigrationModal,
      startMigration,
      handleMigrationComplete,
      refreshStatus
    };
  }
};
</script>
