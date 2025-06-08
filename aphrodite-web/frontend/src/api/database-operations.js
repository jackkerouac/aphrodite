// Database operations API service for Aphrodite Web UI

const getBaseUrl = () => {
  // Handle different environments - same logic as other API files
  if (typeof window !== 'undefined') {
    return window.location.origin;
  }
  return 'http://localhost:5000';
};

const BASE_URL = getBaseUrl();

export const databaseOperations = {
  /**
   * Get database and backup information
   */
  async getBackupInfo() {
    const response = await fetch(`${BASE_URL}/api/database/backup/info`);
    return response.json();
  },

  /**
   * Create a new database backup
   * @param {Object} options - Backup options
   * @param {boolean} options.compress - Whether to compress the backup
   */
  async createBackup(options = {}) {
    const response = await fetch(`${BASE_URL}/api/database/backup/create`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });
    return response.json();
  },

  /**
   * Verify a backup file
   * @param {string} backupFilename - Name of the backup file to verify
   */
  async verifyBackup(backupFilename) {
    const response = await fetch(`${BASE_URL}/api/database/backup/verify`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ backup_filename: backupFilename }),
    });
    return response.json();
  },

  /**
   * Restore database from backup
   * @param {string} backupFilename - Name of the backup file to restore
   */
  async restoreBackup(backupFilename) {
    const response = await fetch(`${BASE_URL}/api/database/backup/restore`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ backup_filename: backupFilename }),
    });
    return response.json();
  },

  /**
   * Clean up old backup files
   * @param {number} keepCount - Number of backups to keep
   */
  async cleanupBackups(keepCount = 5) {
    const response = await fetch(`${BASE_URL}/api/database/backup/cleanup`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ keep_count: keepCount }),
    });
    return response.json();
  },

  /**
   * Export database to JSON
   * @param {Object} options - Export options
   * @param {boolean} options.includeSensitive - Whether to include sensitive data
   */
  async exportDatabase(options = {}) {
    const response = await fetch(`${BASE_URL}/api/database/export`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(options),
    });
    return response.json();
  },

  /**
   * Check database integrity
   */
  async checkIntegrity() {
    const response = await fetch(`${BASE_URL}/api/database/integrity-check`);
    return response.json();
  },
};
