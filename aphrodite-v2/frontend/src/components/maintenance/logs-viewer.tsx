'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Badge } from '@/components/ui/badge';
import { 
  Loader2, 
  Search, 
  RefreshCw, 
  Copy, 
  Trash2, 
  Download,
  FileText,
  Filter,
  AlertCircle,
  Info,
  AlertTriangle,
  Bug
} from 'lucide-react';
import { useLogsViewer } from './hooks';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

export function LogsViewer() {
  const {
    logs,
    fileInfo,
    availableLevels,
    selectedLevel,
    searchQuery,
    isLoading,
    error,
    setSelectedLevel,
    setSearchQuery,
    fetchLogs,
    fetchLogLevels,
    clearLogs,
    copyLogs,
    downloadLogs
  } = useLogsViewer();

  const [showClearModal, setShowClearModal] = useState(false);

  // Load initial data
  useEffect(() => {
    fetchLogLevels();
    fetchLogs();
  }, []);

  // Get CSS class for log level
  const getLogLevelClass = (level: string): string => {
    switch (level?.toLowerCase()) {
      case 'error':
      case 'critical':
        return 'bg-red-500/10 hover:bg-red-500/20';
      case 'warning':
        return 'bg-yellow-500/10 hover:bg-yellow-500/20';
      case 'info':
        return 'bg-blue-500/10 hover:bg-blue-500/20';
      case 'debug':
        return 'bg-purple-500/10 hover:bg-purple-500/20';
      default:
        return 'hover:bg-muted';
    }
  };

  // Get icon for log level
  const getLevelIcon = (level: string) => {
    switch (level?.toLowerCase()) {
      case 'error':
      case 'critical':
        return <AlertCircle className="h-3 w-3 text-red-500" />;
      case 'warning':
        return <AlertTriangle className="h-3 w-3 text-yellow-500" />;
      case 'info':
        return <Info className="h-3 w-3 text-blue-500" />;
      case 'debug':
        return <Bug className="h-3 w-3 text-purple-500" />;
      default:
        return <FileText className="h-3 w-3 text-muted-foreground" />;
    }
  };

  // Get badge variant for log level
  const getLevelBadgeVariant = (level: string): "default" | "destructive" | "secondary" | "outline" => {
    switch (level?.toLowerCase()) {
      case 'error':
      case 'critical':
        return 'destructive';
      case 'warning':
        return 'secondary';
      case 'info':
        return 'default';
      default:
        return 'outline';
    }
  };

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return (bytes / Math.pow(k, i)).toFixed(i > 0 ? 1 : 0) + ' ' + sizes[i];
  };

  // Handle search
  const handleSearch = () => {
    fetchLogs();
  };

  // Handle clear logs
  const handleClearLogs = async () => {
    const success = await clearLogs();
    if (success) {
      setShowClearModal(false);
    }
  };

  // Handle key press in search
  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearch();
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileText className="h-5 w-5" />
            Application Logs
          </CardTitle>
          <CardDescription>
            View, filter, and manage Aphrodite application logs
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Controls */}
          <div className="flex flex-wrap gap-4">
            {/* Level Filter */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Log Level</Label>
              <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="All Levels" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  {availableLevels.map((level) => (
                    <SelectItem key={level} value={level}>
                      <div className="flex items-center gap-2">
                        {getLevelIcon(level)}
                        {level}
                      </div>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            {/* Search */}
            <div className="flex-1 min-w-48 space-y-2">
              <Label className="text-sm font-medium">Search Messages</Label>
              <div className="flex gap-2">
                <Input
                  placeholder="Search log messages..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={handleSearchKeyPress}
                  className="flex-1"
                />
                <Button variant="outline" onClick={handleSearch} disabled={isLoading}>
                  <Search className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Actions */}
            <div className="space-y-2">
              <Label className="text-sm font-medium">Actions</Label>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={fetchLogs} 
                  disabled={isLoading}
                  size="sm"
                >
                  {isLoading ? (
                    <Loader2 className="h-4 w-4 animate-spin" />
                  ) : (
                    <RefreshCw className="h-4 w-4" />
                  )}
                </Button>
                <Button 
                  variant="outline" 
                  onClick={copyLogs} 
                  disabled={!logs.length}
                  size="sm"
                >
                  <Copy className="h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  onClick={downloadLogs} 
                  disabled={!logs.length}
                  size="sm"
                >
                  <Download className="h-4 w-4" />
                </Button>
                <Button 
                  variant="outline" 
                  onClick={() => setShowClearModal(true)} 
                  disabled={!logs.length}
                  size="sm"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>

          {/* File Info */}
          {fileInfo && (
            <Card className="bg-blue-50 dark:bg-blue-950/20 border-blue-200 dark:border-blue-800">
              <CardContent className="p-4">
                <div className="flex justify-between items-center text-sm">
                  <span>
                    <strong>{fileInfo.total_lines}</strong> total lines
                    {logs.length !== fileInfo.total_lines && (
                      <span className="text-muted-foreground">
                        {' '}(showing <strong>{logs.length}</strong> filtered)
                      </span>
                    )}
                  </span>
                  <div className="flex gap-4 text-muted-foreground">
                    <span>{formatFileSize(fileInfo.file_size)}</span>
                    <span>Modified: {new Date(fileInfo.file_modified).toLocaleString()}</span>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Loading State */}
          {isLoading && (
            <div className="flex items-center justify-center p-8">
              <Loader2 className="h-8 w-8 animate-spin mr-2" />
              <span>Loading logs...</span>
            </div>
          )}

          {/* Error State */}
          {error && !isLoading && (
            <Card className="bg-red-50 dark:bg-red-950/20 border-red-200 dark:border-red-800">
              <CardContent className="p-4">
                <div className="flex items-center gap-2 text-red-600 dark:text-red-400">
                  <AlertCircle className="h-5 w-5" />
                  <span className="font-medium">Error loading logs</span>
                </div>
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">{error}</p>
              </CardContent>
            </Card>
          )}

          {/* Empty State */}
          {!logs.length && !isLoading && !error && (
            <Card className="bg-muted/50">
              <CardContent className="p-8 text-center">
                <FileText className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                <h3 className="text-lg font-medium mb-2">No logs found</h3>
                <p className="text-muted-foreground">
                  {(selectedLevel && selectedLevel !== 'all') || searchQuery ? (
                    'Try adjusting your filters or search query.'
                  ) : (
                    'The log file is empty or doesn\'t exist yet.'
                  )}
                </p>
              </CardContent>
            </Card>
          )}

          {/* Logs Display */}
          {logs.length > 0 && !isLoading && (
            <Card>
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">Log Entries</CardTitle>
                  <Badge variant="outline">
                    {logs.length} {logs.length === 1 ? 'entry' : 'entries'}
                  </Badge>
                </div>
              </CardHeader>
              <CardContent className="p-0">
                <div className="max-h-96 overflow-auto border-t">
                  {logs.map((log) => (
                    <div 
                      key={log.line_number} 
                      className={`flex items-start p-3 border-b last:border-b-0 font-mono text-sm transition-colors ${getLogLevelClass(log.level)}`}
                    >
                      <span className="text-xs text-muted-foreground w-12 flex-shrink-0 mr-3 mt-0.5">
                        {log.line_number}
                      </span>
                      <span className="text-xs text-muted-foreground w-32 flex-shrink-0 mr-3 mt-0.5">
                        {log.timestamp}
                      </span>
                      <div className="w-20 flex-shrink-0 mr-3">
                        <Badge 
                          variant={getLevelBadgeVariant(log.level)}
                          className="text-xs font-bold flex items-center gap-1"
                        >
                          {getLevelIcon(log.level)}
                          {log.level}
                        </Badge>
                      </div>
                      <span className="flex-1 break-words leading-relaxed">
                        {log.message}
                      </span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>

      {/* Clear Confirmation Modal */}
      {showClearModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <Card className="w-full max-w-md mx-4">
            <CardHeader>
              <CardTitle className="text-yellow-600">Clear Logs</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p>Are you sure you want to clear all logs? This action cannot be undone.</p>
              <div className="flex gap-2 justify-end">
                <Button 
                  variant="outline" 
                  onClick={() => setShowClearModal(false)}
                >
                  Cancel
                </Button>
                <Button 
                  variant="destructive"
                  onClick={handleClearLogs}
                >
                  Clear All Logs
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
}
