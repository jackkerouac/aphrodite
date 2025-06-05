import { ref, onMounted } from 'vue';
import axios from 'axios';

export function useMigration() {
  const migrationNeeded = ref(false);
  const isChecking = ref(false);
  const checkError = ref(null);
  
  const checkMigrationStatus = async () => {
    isChecking.value = true;
    checkError.value = null;
    
    try {
      const response = await axios.get('/api/settings/migration/status');
      migrationNeeded.value = response.data.migrationNeeded;
      
      console.log('Migration status:', response.data);
      
      return response.data;
    } catch (error) {
      console.error('Error checking migration status:', error);
      checkError.value = error.response?.data?.message || error.message || 'Failed to check migration status';
      migrationNeeded.value = false;
    } finally {
      isChecking.value = false;
    }
  };
  
  const startMigration = async () => {
    try {
      const response = await axios.post('/api/settings/migration/start');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || error.message || 'Failed to start migration');
    }
  };
  
  const finalizeMigration = async () => {
    try {
      const response = await axios.post('/api/settings/migration/finalize');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || error.message || 'Failed to finalize migration');
    }
  };
  
  const rollbackMigration = async () => {
    try {
      const response = await axios.post('/api/settings/migration/rollback');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || error.message || 'Failed to rollback migration');
    }
  };
  
  // Auto-check migration status on mount
  onMounted(() => {
    checkMigrationStatus();
  });
  
  return {
    migrationNeeded,
    isChecking,
    checkError,
    checkMigrationStatus,
    startMigration,
    finalizeMigration,
    rollbackMigration
  };
}
