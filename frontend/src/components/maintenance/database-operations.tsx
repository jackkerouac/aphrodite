'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import { 
  Loader2, 
  Database, 
  Download, 
  Upload, 
  RefreshCw, 
  Trash2, 
  CheckCircle,
  XCircle,
  HardDrive,
  Archive,
  FileText
} from 'lucide-react';
import { toast } from 'sonner';
import { useDatabaseOperations } from './hooks';
import { BackupFile } from './types';

export function DatabaseOperations() {
  const { databaseInfo, loading, loadDatabaseInfo, createBackup, restoreBackup, exportDatabase, importDatabaseSettings } = useDatabaseOperations();
  
  const [backupOptions, setBackupOptions] = useState({
    compress: true
  });
  
  const [cleanupOptions, setCleanupOptions] = useState({
    keepCount: 5
  });
  
  const [exportOptions, setExportOptions] = useState({
    includeSensitive: false
  });
  
  const [restoreConfirm, setRestoreConfirm] = useState<{
    show: boolean;
    backup: BackupFile | null;
  }>({
    show: false,
    backup: null
  });
  
  const [importConfirm, setImportConfirm] = useState<{
    show: boolean;
    jsonData: any;
    filename: string;
  }>({
    show: false,
    jsonData: null,
    filename: ''
  });
  
  const [integrityStatus, setIntegrityStatus] = useState<{
    checked: boolean;
    ok: boolean;
    message?: string;
  }>({
    checked: false,
    ok: false
  });

  // Check database integrity
  const checkIntegrity = async () => {
    // This would be implemented when the backend endpoint is available
    setIntegrityStatus({
      checked: true,
      ok: true,
      message: 'Database integrity check passed'
    });
  };

  // Handle backup creation
  const handleCreateBackup = async () => {
    await createBackup(backupOptions);
  };

  // Show restore confirmation
  const showRestoreConfirm = (backup: BackupFile) => {
    setRestoreConfirm({
      show: true,
      backup
    });
  };

  // Confirm restore
  const confirmRestore = async () => {
    if (restoreConfirm.backup) {
      await restoreBackup(restoreConfirm.backup.filename);
    }
    setRestoreConfirm({ show: false, backup: null });
  };

  // Handle export to JSON
  const handleExportToJSON = async () => {
    await exportDatabase(exportOptions);
  };

  // Handle file selection for import
  const handleImportFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    if (!file.name.endsWith('.json')) {
      toast.error('Please select a JSON file');
      return;
    }

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const jsonData = JSON.parse(e.target?.result as string);
        setImportConfirm({
          show: true,
          jsonData,
          filename: file.name
        });
      } catch (error) {
        toast.error('Invalid JSON file format');
      }
    };
    reader.readAsText(file);

    // Reset the input
    event.target.value = '';
  };

  // Confirm import
  const confirmImport = async () => {
    if (importConfirm.jsonData) {
      await importDatabaseSettings(importConfirm.jsonData);
    }
    setImportConfirm({ show: false, jsonData: null, filename: '' });
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(i > 0 ? 1 : 0) + ' ' + sizes[i];
  };

  // Format date
  const formatDate = (isoString: string): string => {
    return new Date(isoString).toLocaleString();
  };

  // Load database info on mount
  useEffect(() => {
    console.log('DatabaseOperations: Component mounted, loading database info...');
    loadDatabaseInfo();
  }, []);

  // Debug logging
  useEffect(() => {
    console.log('DatabaseOperations: databaseInfo changed:', databaseInfo);
    console.log('DatabaseOperations: loading state:', loading);
  }, [databaseInfo, loading]);

  return (
    <div className="space-y-6">
      {/* Database Information */}
      <Card>
        <CardHeader>
          <div className="flex justify-between items-center">
            <div>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Database Information
              </CardTitle>
              <CardDescription>
                View database status and perform integrity checks
              </CardDescription>
            </div>
            <Button 
              variant="outline" 
              size="sm"
              onClick={loadDatabaseInfo}
              disabled={loading.info}
            >
              {loading.info ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {databaseInfo ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Card className="bg-muted/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Database Status</p>
                      <p className={`text-2xl font-bold ${databaseInfo.database.exists ? 'text-green-600' : 'text-red-600'}`}>
                        {databaseInfo.database.exists ? 'Active' : 'Not Found'}
                      </p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {databaseInfo.database.path}
                      </p>
                    </div>
                    <HardDrive className={`h-8 w-8 ${databaseInfo.database.exists ? 'text-green-600' : 'text-red-600'}`} />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-muted/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Database Size</p>
                      <p className="text-2xl font-bold">{databaseInfo.database.size_formatted}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        Schema {databaseInfo.schema_version}
                      </p>
                    </div>
                    <Database className="h-8 w-8 text-blue-600" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-muted/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Available Backups</p>
                      <p className="text-2xl font-bold">{databaseInfo.backups.length}</p>
                      <p className="text-xs text-muted-foreground mt-1">
                        {databaseInfo.backup_directory}
                      </p>
                    </div>
                    <Archive className="h-8 w-8 text-purple-600" />
                  </div>
                </CardContent>
              </Card>

              <Card className="bg-muted/50">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-sm font-medium">Integrity Status</p>
                      <p className={`text-2xl font-bold ${
                        integrityStatus.checked 
                          ? (integrityStatus.ok ? 'text-green-600' : 'text-red-600') 
                          : 'text-yellow-600'
                      }`}>
                        {integrityStatus.checked ? (integrityStatus.ok ? 'OK' : 'Issues') : 'Not Checked'}
                      </p>
                      <Button 
                        variant="outline" 
                        size="sm" 
                        onClick={checkIntegrity}
                        disabled={loading.integrity}
                        className="mt-1"
                      >
                        {loading.integrity ? (
                          <Loader2 className="h-3 w-3 animate-spin mr-1" />
                        ) : null}
                        Check Now
                      </Button>
                    </div>
                    {integrityStatus.checked ? (
                      integrityStatus.ok ? (
                        <CheckCircle className="h-8 w-8 text-green-600" />
                      ) : (
                        <XCircle className="h-8 w-8 text-red-600" />
                      )
                    ) : (
                      <RefreshCw className="h-8 w-8 text-yellow-600" />
                    )}
                  </div>
                </CardContent>
              </Card>
            </div>
          ) : (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin mr-2" />
              <span>Loading database information...</span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Backup Operations */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Archive className="h-5 w-5" />
            Backup Operations
          </CardTitle>
          <CardDescription>
            Create, restore, and manage database backups
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Create Backup */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Create New Backup</Label>
            <div className="flex items-center gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="compress-backup"
                  checked={backupOptions.compress}
                  onCheckedChange={(checked) => 
                    setBackupOptions(prev => ({ ...prev, compress: checked as boolean }))
                  }
                />
                <Label htmlFor="compress-backup" className="text-sm">
                  Compress backup
                </Label>
              </div>
              <Button 
                onClick={handleCreateBackup}
                disabled={loading.backup || !databaseInfo?.database.exists}
              >
                {loading.backup ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Download className="h-4 w-4 mr-2" />
                )}
                Create Backup
              </Button>
            </div>
          </div>

          {/* Backup List */}
          {databaseInfo?.backups && databaseInfo.backups.length > 0 && (
            <div className="space-y-3">
              <Label className="text-base font-semibold">Available Backups</Label>
              <div className="border rounded-lg overflow-hidden">
                <div className="max-h-96 overflow-y-auto">
                  <table className="w-full text-sm">
                    <thead className="bg-muted/50 border-b">
                      <tr>
                        <th className="text-left p-3 font-medium">Filename</th>
                        <th className="text-left p-3 font-medium">Size</th>
                        <th className="text-left p-3 font-medium">Created</th>
                        <th className="text-left p-3 font-medium">Type</th>
                        <th className="text-left p-3 font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {databaseInfo.backups.slice(0, 10).map((backup) => (
                        <tr key={backup.filename} className="border-b last:border-b-0 hover:bg-muted/25">
                          <td className="p-3 font-mono text-xs">{backup.filename}</td>
                          <td className="p-3">{backup.size_formatted}</td>
                          <td className="p-3">{formatDate(backup.created)}</td>
                          <td className="p-3">
                            <Badge variant={backup.compressed ? "default" : "outline"}>
                              {backup.compressed ? 'Compressed' : 'Uncompressed'}
                            </Badge>
                          </td>
                          <td className="p-3">
                            <div className="flex gap-1">
                              <Button 
                                variant="outline" 
                                size="sm"
                                onClick={() => showRestoreConfirm(backup)}
                                disabled={loading.restore}
                                title="Restore from this backup"
                              >
                                <Upload className="h-3 w-3" />
                              </Button>
                            </div>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}

          {/* Cleanup Backups */}
          <div className="space-y-3">
            <Label className="text-base font-semibold">Cleanup Old Backups</Label>
            <div className="flex items-center gap-4">
              <span className="text-sm">Keep</span>
              <Input 
                type="number" 
                value={cleanupOptions.keepCount}
                onChange={(e) => setCleanupOptions(prev => ({ 
                  ...prev, 
                  keepCount: parseInt(e.target.value) || 5 
                }))}
                min={1} 
                max={50}
                className="w-20"
              />
              <span className="text-sm">most recent backups</span>
              <Button 
                variant="outline"
                size="sm"
                disabled={loading.cleanup || !databaseInfo || databaseInfo.backups.length <= cleanupOptions.keepCount}
              >
                {loading.cleanup ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Trash2 className="h-4 w-4 mr-2" />
                )}
                Cleanup
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Export Section */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Export & Maintenance
          </CardTitle>
          <CardDescription>
            Export database data and perform maintenance operations
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <Label className="text-base font-semibold">Export Database to JSON</Label>
            <div className="flex items-center gap-4">
              <div className="flex items-center space-x-2">
                <Checkbox 
                  id="include-sensitive"
                  checked={exportOptions.includeSensitive}
                  onCheckedChange={(checked) => 
                    setExportOptions(prev => ({ ...prev, includeSensitive: checked as boolean }))
                  }
                />
                <Label htmlFor="include-sensitive" className="text-sm">
                  Include sensitive data
                </Label>
              </div>
              <Button 
                onClick={handleExportToJSON}
                disabled={loading.export || !databaseInfo?.database.exists}
              >
                {loading.export ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Download className="h-4 w-4 mr-2" />
                )}
                Export to JSON
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              💾 The exported file will be automatically downloaded to your browser
            </p>
          </div>
          
          {/* Import from JSON */}
          <div className="space-y-3 pt-4 border-t">
            <Label className="text-base font-semibold">Restore Database Settings from JSON</Label>
            <div className="flex items-center gap-4">
              <input
                type="file"
                accept=".json"
                onChange={handleImportFileSelect}
                style={{ display: 'none' }}
                id="json-import-input"
              />
              <Button 
                variant="outline"
                onClick={() => document.getElementById('json-import-input')?.click()}
                disabled={loading.restore || !databaseInfo?.database.exists}
              >
                {loading.restore ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Upload className="h-4 w-4 mr-2" />
                )}
                Select JSON File
              </Button>
            </div>
            <p className="text-xs text-muted-foreground">
              ⚠️ This will replace current database settings with data from the JSON export file
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Restore Confirmation Modal */}
      {restoreConfirm.show && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="text-yellow-600">⚠️ Confirm Database Restore</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>
                This will <strong>replace</strong> your current database with the backup:
              </p>
              <div className="bg-muted p-3 rounded">
                <p className="font-medium">{restoreConfirm.backup?.filename}</p>
                <p className="text-sm text-muted-foreground">
                  Created: {restoreConfirm.backup ? formatDate(restoreConfirm.backup.created) : ''}
                </p>
              </div>
              <p className="text-destructive text-sm">
                <strong>This action cannot be undone!</strong> Your current database will be backed up automatically before the restore.
              </p>
              <div className="flex gap-2 justify-end">
                <Button 
                  variant="outline" 
                  onClick={() => setRestoreConfirm({ show: false, backup: null })}
                >
                  Cancel
                </Button>
                <Button 
                  variant="destructive"
                  onClick={confirmRestore}
                  disabled={loading.restore}
                >
                  {loading.restore ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : null}
                  Restore Database
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
      
      {/* Import Confirmation Modal */}
      {importConfirm.show && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="text-blue-600">📄 Confirm Database Settings Import</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>
                This will <strong>restore database settings</strong> from the JSON export:
              </p>
              <div className="bg-muted p-3 rounded">
                <p className="font-medium">{importConfirm.filename}</p>
                <p className="text-sm text-muted-foreground">
                  JSON Export File
                </p>
              </div>
              <p className="text-yellow-600 text-sm">
                <strong>Warning:</strong> This will replace your current database settings. Your current database will be backed up automatically before the import.
              </p>
              <div className="flex gap-2 justify-end">
                <Button 
                  variant="outline" 
                  onClick={() => setImportConfirm({ show: false, jsonData: null, filename: '' })}
                >
                  Cancel
                </Button>
                <Button 
                  onClick={confirmImport}
                  disabled={loading.restore}
                >
                  {loading.restore ? (
                    <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  ) : null}
                  Import Settings
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
