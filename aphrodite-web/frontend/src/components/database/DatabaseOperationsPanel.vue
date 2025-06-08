<template>
  <div class="database-operations">
    <!-- Database Information Section -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <div class="flex justify-between items-center mb-4">
          <h2 class="card-title">Database Information</h2>
          <button 
            class="btn btn-sm btn-outline" 
            @click="refreshInfo"
            :disabled="loading.info"
          >
            <span v-if="loading.info" class="loading loading-spinner loading-xs"></span>
            <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh
          </button>
        </div>

        <div v-if="databaseInfo" class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div class="stat bg-base-200 rounded-lg">
            <div class="stat-title">Database Status</div>
            <div class="stat-value text-lg" :class="databaseInfo.database.exists ? 'text-success' : 'text-error'">
              {{ databaseInfo.database.exists ? 'Active' : 'Not Found' }}
            </div>
            <div class="stat-desc">{{ databaseInfo.database.path }}</div>
          </div>

          <div class="stat bg-base-200 rounded-lg">
            <div class="stat-title">Database Size</div>
            <div class="stat-value text-lg">{{ databaseInfo.database.size_formatted }}</div>
            <div class="stat-desc">Schema {{ databaseInfo.schema_version }}</div>
          </div>

          <div class="stat bg-base-200 rounded-lg">
            <div class="stat-title">Available Backups</div>
            <div class="stat-value text-lg">{{ databaseInfo.backups.length }}</div>
            <div class="stat-desc">{{ databaseInfo.backup_directory }}</div>
          </div>

          <div class="stat bg-base-200 rounded-lg">
            <div class="stat-title">Integrity Status</div>
            <div class="stat-value text-lg" :class="integrityStatus.checked ? (integrityStatus.ok ? 'text-success' : 'text-error') : 'text-warning'">
              {{ integrityStatus.checked ? (integrityStatus.ok ? 'OK' : 'Issues') : 'Not Checked' }}
            </div>
            <div class="stat-desc">
              <button 
                class="btn btn-xs btn-outline" 
                @click="checkIntegrity"
                :disabled="loading.integrity"
              >
                <span v-if="loading.integrity" class="loading loading-spinner loading-xs"></span>
                Check Now
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Backup Operations Section -->
    <div class="card bg-base-100 shadow-xl mb-6">
      <div class="card-body">
        <h2 class="card-title mb-4">Backup Operations</h2>

        <!-- Create Backup -->
        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-semibold">Create New Backup</span>
          </label>
          <div class="flex gap-2 items-center">
            <label class="label cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-sm mr-2" 
                v-model="backupOptions.compress"
              />
              <span class="label-text">Compress backup</span>
            </label>
            <button 
              class="btn btn-primary" 
              @click="createBackup"
              :disabled="loading.backup || !databaseInfo?.database.exists"
            >
              <span v-if="loading.backup" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3-3m0 0l-3 3m3-3v12" />
              </svg>
              Create Backup
            </button>
          </div>
        </div>

        <!-- Backup List -->
        <div v-if="databaseInfo?.backups.length > 0" class="mb-4">
          <h3 class="font-semibold mb-2">Available Backups</h3>
          <div class="overflow-x-auto">
            <table class="table table-sm">
              <thead>
                <tr>
                  <th>Filename</th>
                  <th>Size</th>
                  <th>Created</th>
                  <th>Type</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="backup in databaseInfo.backups.slice(0, 10)" :key="backup.filename">
                  <td class="font-mono text-sm">{{ backup.filename }}</td>
                  <td>{{ backup.size_formatted }}</td>
                  <td>{{ formatDate(backup.created) }}</td>
                  <td>
                    <span class="badge badge-sm" :class="backup.compressed ? 'badge-primary' : 'badge-neutral'">
                      {{ backup.compressed ? 'Compressed' : 'Uncompressed' }}
                    </span>
                  </td>
                  <td>
                    <div class="flex gap-1">
                      <button 
                        class="btn btn-xs btn-outline btn-info" 
                        @click="verifyBackup(backup.filename)"
                        :disabled="loading.verify"
                        title="Verify backup integrity"
                      >
                        <span v-if="loading.verify === backup.filename" class="loading loading-spinner loading-xs"></span>
                        <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                      </button>
                      <button 
                        class="btn btn-xs btn-outline btn-warning" 
                        @click="showRestoreConfirm(backup)"
                        :disabled="loading.restore"
                        title="Restore from this backup"
                      >
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
                        </svg>
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Cleanup Backups -->
        <div class="form-control">
          <label class="label">
            <span class="label-text font-semibold">Cleanup Old Backups</span>
          </label>
          <div class="flex gap-2 items-center">
            <span class="text-sm">Keep</span>
            <input 
              type="number" 
              class="input input-sm input-bordered w-20" 
              v-model.number="cleanupOptions.keepCount"
              min="1" 
              max="50"
            />
            <span class="text-sm">most recent backups</span>
            <button 
              class="btn btn-sm btn-outline btn-error" 
              @click="cleanupBackups"
              :disabled="loading.cleanup || databaseInfo?.backups.length <= cleanupOptions.keepCount"
            >
              <span v-if="loading.cleanup" class="loading loading-spinner loading-xs"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
              </svg>
              Cleanup
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Section -->
    <div class="card bg-base-100 shadow-xl">
      <div class="card-body">
        <h2 class="card-title mb-4">Export & Maintenance</h2>

        <div class="form-control mb-4">
          <label class="label">
            <span class="label-text font-semibold">Export Database to JSON</span>
          </label>
          <div class="flex gap-2 items-center">
            <label class="label cursor-pointer">
              <input 
                type="checkbox" 
                class="checkbox checkbox-sm mr-2" 
                v-model="exportOptions.includeSensitive"
              />
              <span class="label-text">Include sensitive data</span>
            </label>
            <button 
              class="btn btn-outline" 
              @click="exportDatabase"
              :disabled="loading.export || !databaseInfo?.database.exists"
            >
              <span v-if="loading.export" class="loading loading-spinner loading-sm"></span>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              Export to JSON
            </button>
          </div>
          <div class="label">
            <span class="label-text-alt text-info">
              💾 The exported file will be automatically downloaded to your browser
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- Restore Confirmation Modal -->
    <div v-if="restoreConfirm.show" class="modal modal-open">
      <div class="modal-box">
        <h3 class="font-bold text-lg text-warning">⚠️ Confirm Database Restore</h3>
        <p class="py-4">
          This will <strong>replace</strong> your current database with the backup:
          <br><br>
          <strong>{{ restoreConfirm.backup?.filename }}</strong>
          <br>
          Created: {{ formatDate(restoreConfirm.backup?.created) }}
          <br><br>
          <span class="text-error">This action cannot be undone!</span>
          Your current database will be backed up automatically before the restore.
        </p>
        <div class="modal-action">
          <button class="btn btn-ghost" @click="restoreConfirm.show = false">Cancel</button>
          <button 
            class="btn btn-warning" 
            @click="confirmRestore"
            :disabled="loading.restore"
          >
            <span v-if="loading.restore" class="loading loading-spinner loading-sm"></span>
            Restore Database
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { databaseOperations } from '@/api/database-operations';

export default {
  name: 'DatabaseOperationsPanel',
  emits: ['operation-completed'],
  setup(props, { emit }) {
    const databaseInfo = ref(null);
    const integrityStatus = ref({ checked: false, ok: false });
    
    const loading = ref({
      info: false,
      backup: false,
      restore: false,
      verify: false,
      cleanup: false,
      export: false,
      integrity: false
    });
    
    const backupOptions = ref({
      compress: true
    });
    
    const cleanupOptions = ref({
      keepCount: 5
    });
    
    const exportOptions = ref({
      includeSensitive: false
    });
    
    const restoreConfirm = ref({
      show: false,
      backup: null
    });
    
    // Load database info on mount
    const refreshInfo = async () => {
      loading.value.info = true;
      try {
        const response = await databaseOperations.getBackupInfo();
        if (response.success) {
          databaseInfo.value = response;
        } else {
          emit('operation-completed', {
            success: false,
            message: `Failed to load database info: ${response.error}`
          });
        }
      } catch (error) {
        emit('operation-completed', {
          success: false,
          message: `Error loading database info: ${error.message}`
        });
      } finally {
        loading.value.info = false;
      }
    };
    
    // Create backup
    const createBackup = async () => {
      loading.value.backup = true;
      try {
        const response = await databaseOperations.createBackup(backupOptions.value);
        if (response.success) {
          emit('operation-completed', {
            success: true,
            message: `Backup created successfully: ${response.backup_filename}`,
            details: {
              filename: response.backup_filename,
              size: response.backup_size,
              compressed: response.compressed,
              compression_ratio: response.compression_ratio
            }
          });
          // Refresh info to show new backup
          await refreshInfo();
        } else {
          emit('operation-completed', {
            success: false,
            message: `Backup failed: ${response.error}`
          });
        }
      } catch (error) {
        emit('operation-completed', {
          success: false,
          message: `Error creating backup: ${error.message}`
        });
      } finally {
        loading.value.backup = false;
      }
    };
    
    // Verify backup
    const verifyBackup = async (filename) => {
      loading.value.verify = filename;
      try {
        const response = await databaseOperations.verifyBackup(filename);
        if (response.success) {
          emit('operation-completed', {
            success: response.valid,
            message: response.valid 
              ? `Backup ${filename} is valid ✅` 
              : `Backup ${filename} verification failed ❌`
          });
        } else {
          emit('operation-completed', {
            success: false,
            message: `Verification failed: ${response.error}`
          });
        }
      } catch (error) {
        emit('operation-completed', {
          success: false,
          message: `Error verifying backup: ${error.message}`
        });
      } finally {
        loading.value.verify = false;
      }
    };
    
    // Show restore confirmation
    const showRestoreConfirm = (backup) => {
      restoreConfirm.value.backup = backup;
      restoreConfirm.value.show = true;
    };
    
    // Confirm restore
    const confirmRestore = async () => {
      loading.value.restore = true;
      try {
        const response = await databaseOperations.restoreBackup(restoreConfirm.value.backup.filename);
        if (response.success) {
          emit('operation-completed', {
            success: true,
            message: response.message
          });
          // Refresh info after restore
          await refreshInfo();
        } else {
          emit('operation-completed', {
            success: false,
            message: `Restore failed: ${response.error}`
          });
        }
      } catch (error) {
        emit('operation-completed', {
          success: false,
          message: `Error during restore: ${error.message}`
        });
      } finally {
        loading.value.restore = false;
        restoreConfirm.value.show = false;
      }
    };
    
    // Cleanup old backups
    const cleanupBackups = async () => {
      loading.value.cleanup = true;
      try {
        const response = await databaseOperations.cleanupBackups(cleanupOptions.value.keepCount);
        if (response.success) {
          emit('operation-completed', {
            success: true,
            message: response.message,
            details: {
              removed_count: response.removed_count,
              kept_count: response.kept_count
            }
          });
          // Refresh info to show updated backup list
          await refreshInfo();
        } else {
          emit('operation-completed', {
            success: false,
            message: `Cleanup failed: ${response.error}`
          });
        }
      } catch (error) {
        emit('operation-completed', {
          success: false,
          message: `Error during cleanup: ${error.message}`
        });
      } finally {
        loading.value.cleanup = false;
      }
    };
    
    // Export database
    const exportDatabase = async () => {
      loading.value.export = true;
      try {
        const response = await databaseOperations.exportDatabase(exportOptions.value);
        if (response.success) {
          emit('operation-completed', {
            success: true,
            message: `Database exported: ${response.export_filename}`,
            details: {
              filename: response.export_filename,
              size: response.export_size_formatted,
              include_sensitive: response.include_sensitive
            }
          });
          
          // Automatically download the exported file
          if (response.download_url) {
            // Small delay to let the success message show
            setTimeout(() => {
              databaseOperations.downloadExportFile(response.export_filename);
            }, 500);
          }
        } else {
          emit('operation-completed', {
            success: false,
            message: `Export failed: ${response.error}`
          });
        }
      } catch (error) {
        emit('operation-completed', {
          success: false,
          message: `Error during export: ${error.message}`
        });
      } finally {
        loading.value.export = false;
      }
    };
    
    // Check database integrity
    const checkIntegrity = async () => {
      loading.value.integrity = true;
      try {
        const response = await databaseOperations.checkIntegrity();
        if (response.success) {
          integrityStatus.value = {
            checked: true,
            ok: response.integrity_ok
          };
          
          emit('operation-completed', {
            success: response.integrity_ok,
            message: response.integrity_ok 
              ? 'Database integrity check passed ✅' 
              : `Database integrity issues found: ${response.result}`,
            details: response.database_info
          });
        } else {
          integrityStatus.value = {
            checked: true,
            ok: false
          };
          
          emit('operation-completed', {
            success: false,
            message: `Integrity check failed: ${response.error}`
          });
        }
      } catch (error) {
        emit('operation-completed', {
          success: false,
          message: `Error checking integrity: ${error.message}`
        });
      } finally {
        loading.value.integrity = false;
      }
    };
    
    // Format date for display
    const formatDate = (isoString) => {
      if (!isoString) return 'Unknown';
      return new Date(isoString).toLocaleString();
    };
    
    // Load initial data
    onMounted(() => {
      refreshInfo();
    });
    
    return {
      databaseInfo,
      integrityStatus,
      loading,
      backupOptions,
      cleanupOptions,
      exportOptions,
      restoreConfirm,
      refreshInfo,
      createBackup,
      verifyBackup,
      showRestoreConfirm,
      confirmRestore,
      cleanupBackups,
      exportDatabase,
      checkIntegrity,
      formatDate
    };
  }
};
</script>
