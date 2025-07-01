'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Clock, CheckCircle, XCircle, AlertCircle, RefreshCw, Trash2 } from 'lucide-react';
import { apiService } from '@/services/api';
import { toast } from 'sonner';

interface ScheduleExecution {
  id: string;
  schedule_id: string;
  status: string;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
  items_processed?: string;
  created_at: string;
}

export function ScheduleHistory() {
  const [executions, setExecutions] = useState<ScheduleExecution[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [clearingHistory, setClearingHistory] = useState(false);
  const [showClearDialog, setShowClearDialog] = useState(false);

  const fetchHistory = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 50 };
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response = await apiService.getScheduleHistory(params);
      setExecutions(response);
    } catch (error) {
      console.error('Failed to fetch schedule history:', error);
      toast.error('Failed to load schedule history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [statusFilter]);

  const handleClearHistory = async () => {
    try {
      setClearingHistory(true);
      const result = await apiService.clearScheduleHistory();
      toast.success(`${result.message}`);
      await fetchHistory(); // Refresh the history list
      setShowClearDialog(false);
    } catch (error) {
      console.error('Failed to clear schedule history:', error);
      toast.error('Failed to clear schedule history');
    } finally {
      setClearingHistory(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <XCircle className="h-4 w-4 text-red-500" />;
      case 'running':
        return <RefreshCw className="h-4 w-4 text-blue-500 animate-spin" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusVariant = (status: string): 'default' | 'secondary' | 'destructive' | 'outline' => {
    switch (status) {
      case 'completed':
        return 'default';
      case 'failed':
        return 'destructive';
      case 'running':
        return 'secondary';
      case 'pending':
        return 'outline';
      default:
        return 'secondary';
    }
  };

  const formatDateTime = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  const formatDuration = (started: string, completed?: string) => {
    const start = new Date(started);
    const end = completed ? new Date(completed) : new Date();
    const duration = Math.round((end.getTime() - start.getTime()) / 1000);
    
    if (duration < 60) {
      return `${duration}s`;
    } else if (duration < 3600) {
      return `${Math.floor(duration / 60)}m ${duration % 60}s`;
    } else {
      const hours = Math.floor(duration / 3600);
      const minutes = Math.floor((duration % 3600) / 60);
      return `${hours}h ${minutes}m`;
    }
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold">Schedule History</h2>
        </div>
        <div className="text-center py-8">
          <Clock className="h-8 w-8 mx-auto mb-2 animate-spin" />
          <p>Loading history...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Schedule History</h2>
        <div className="flex items-center gap-2">
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Status</SelectItem>
              <SelectItem value="completed">Completed</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
              <SelectItem value="running">Running</SelectItem>
              <SelectItem value="pending">Pending</SelectItem>
            </SelectContent>
          </Select>
          <Button variant="outline" onClick={fetchHistory}>
            <RefreshCw className="h-4 w-4 mr-2" />
            Refresh
          </Button>
          <Button 
            variant="outline" 
            onClick={() => setShowClearDialog(true)}
            disabled={clearingHistory || executions.length === 0}
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Clear History
          </Button>
        </div>
      </div>

      {executions.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <Clock className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">No execution history</h3>
            <p className="text-muted-foreground">
              Schedule executions will appear here once they start running
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {executions.map((execution) => (
            <Card key={execution.id}>
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="space-y-1">
                    <CardTitle className="flex items-center gap-2 text-base">
                      {getStatusIcon(execution.status)}
                      Execution {execution.id.slice(0, 8)}
                      <Badge variant={getStatusVariant(execution.status)}>
                        {execution.status.charAt(0).toUpperCase() + execution.status.slice(1)}
                      </Badge>
                    </CardTitle>
                    <CardDescription>
                      Created: {formatDateTime(execution.created_at)}
                    </CardDescription>
                  </div>
                  <div className="text-right text-sm text-muted-foreground">
                    {execution.started_at && (
                      <div>
                        Duration: {formatDuration(execution.started_at, execution.completed_at)}
                      </div>
                    )}
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="space-y-2 text-sm">
                  {execution.started_at && (
                    <div>
                      <span className="font-medium">Started: </span>
                      <span className="text-muted-foreground">
                        {formatDateTime(execution.started_at)}
                      </span>
                    </div>
                  )}
                  {execution.completed_at && (
                    <div>
                      <span className="font-medium">Completed: </span>
                      <span className="text-muted-foreground">
                        {formatDateTime(execution.completed_at)}
                      </span>
                    </div>
                  )}
                  {execution.items_processed && (
                    <div>
                      <span className="font-medium">Items Processed: </span>
                      <span className="text-muted-foreground">
                        {execution.items_processed}
                      </span>
                    </div>
                  )}
                  {execution.error_message && (
                    <div className="p-2 bg-destructive/10 rounded border">
                      <span className="font-medium text-destructive">Error: </span>
                      <span className="text-destructive text-xs">
                        {execution.error_message}
                      </span>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Clear History Confirmation Dialog */}
      <Dialog open={showClearDialog} onOpenChange={setShowClearDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Clear Schedule History</DialogTitle>
            <DialogDescription>
              Are you sure you want to clear all schedule execution history? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowClearDialog(false)}
              disabled={clearingHistory}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleClearHistory}
              disabled={clearingHistory}
            >
              {clearingHistory ? (
                <>
                  <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                  Clearing...
                </>
              ) : (
                <>
                  <Trash2 className="h-4 w-4 mr-2" />
                  Clear History
                </>
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
