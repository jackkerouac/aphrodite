<template>
  <div v-if="isOpen" class="modal modal-open">
    <div class="modal-box">
      <h3 class="font-bold text-lg mb-4">Database Migration</h3>
      
      <div class="mb-4">
        <p class="text-sm mb-4">
          Aphrodite is upgrading your settings to a new database format. This will improve performance and reliability.
        </p>
        
        <!-- Progress Bar -->
        <div class="w-full bg-base-300 rounded-full h-2.5 mb-4">
          <div 
            class="bg-primary h-2.5 rounded-full transition-all duration-300"
            :style="{ width: progress + '%' }"
          ></div>
        </div>
        
        <!-- Current Step -->
        <div class="flex items-center gap-2 mb-4">
          <div v-if="!migrationComplete && !migrationError" class="loading loading-spinner loading-sm"></div>
          <div v-else-if="migrationComplete" class="text-success">✓</div>
          <div v-else-if="migrationError" class="text-error">✗</div>
          
          <span class="font-semibold">
            {{ currentStepText }}
          </span>
        </div>
        
        <!-- Error Alert -->
        <div v-if="migrationError" class="alert alert-error mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>{{ migrationError }}</span>
        </div>
        
        <!-- Success Alert -->
        <div v-if="migrationComplete" class="alert alert-success mb-4">
          <svg xmlns="http://www.w3.org/2000/svg" class="stroke-current shrink-0 h-6 w-6" fill="none" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span>Your settings have been successfully migrated to the new database format.</span>
        </div>
      </div>
      
      <!-- Actions -->
      <div class="modal-action">
        <button 
          v-if="migrationComplete" 
          @click="handleClose" 
          class="btn btn-primary"
        >
          Continue
          <svg xmlns="http://www.w3.org/2000/svg" class="h-4 w-4 ml-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7l5 5m0 0l-5 5m5-5H6" />
          </svg>
        </button>
        
        <button 
          v-if="migrationError" 
          @click="startMigration" 
          class="btn btn-primary"
        >
          Retry Migration
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'MigrationModal',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close', 'migration-complete'],
  data() {
    return {
      progress: 0,
      migrationStep: 0,
      migrationComplete: false,
      migrationError: null,
      migrationSteps: [
        'Checking migration status...',
        'Migrating settings...',
        'Finalizing migration...'
      ]
    };
  },
  computed: {
    currentStepText() {
      if (this.migrationComplete) {
        return 'Migration Complete!';
      }
      if (this.migrationError) {
        return 'Migration Failed';
      }
      return this.migrationSteps[this.migrationStep] || 'Preparing...';
    }
  },
  watch: {
    isOpen(newValue) {
      if (newValue) {
        this.startMigration();
      }
    }
  },
  methods: {
    async startMigration() {
      this.progress = 0;
      this.migrationStep = 0;
      this.migrationComplete = false;
      this.migrationError = null;
      
      try {
        // Step 1: Check if migration is needed
        this.progress = 10;
        await this.sleep(500);
        
        const statusResponse = await axios.get('/api/settings/migration/status');
        
        if (!statusResponse.data.migrationNeeded) {
          // No migration needed
          this.migrationComplete = true;
          this.progress = 100;
          return;
        }
        
        // Step 2: Start migration
        this.migrationStep = 1;
        this.progress = 40;
        
        await this.sleep(1000);
        
        const migrationResponse = await axios.post('/api/settings/migration/start');
        
        if (!migrationResponse.data.success) {
          throw new Error(migrationResponse.data.message);
        }
        
        // Step 3: Finalize migration
        this.migrationStep = 2;
        this.progress = 80;
        
        await this.sleep(500);
        
        const finalizeResponse = await axios.post('/api/settings/migration/finalize');
        
        if (!finalizeResponse.data.success) {
          throw new Error(finalizeResponse.data.message);
        }
        
        // Migration complete
        this.progress = 100;
        this.migrationComplete = true;
        
        this.$emit('migration-complete');
        
      } catch (error) {
        console.error('Migration error:', error);
        this.migrationError = error.response?.data?.message || error.message || 'An error occurred during migration';
      }
    },
    
    handleClose() {
      this.$emit('close');
    },
    
    sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
    }
  }
};
</script>

<style scoped>
.modal-open {
  display: flex;
}
</style>
