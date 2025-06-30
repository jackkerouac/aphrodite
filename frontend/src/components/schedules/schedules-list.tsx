'use client';

import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { Plus, Edit, Trash2, Play, Clock } from 'lucide-react';
import { apiService } from '@/services/api';
import { toast } from 'sonner';

interface Schedule {
  id: string;
  name: string;
  timezone: string;
  cron_expression: string;
  badge_types: string[];
  reprocess_all: boolean;
  enabled: boolean;
  target_libraries: string[];
  created_at: string;
  updated_at: string;
}

interface SchedulesListProps {
  onCreateSchedule: () => void;
  onEditSchedule: (schedule: Schedule) => void;
}

export function SchedulesList({ onCreateSchedule, onEditSchedule }: SchedulesListProps) {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [scheduleToDelete, setScheduleToDelete] = useState<Schedule | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchSchedules = async () => {
    try {
      setLoading(true);
      const response = await apiService.getSchedules();
      setSchedules(response);
    } catch (error) {
      console.error('Failed to fetch schedules:', error);
      toast.error('Failed to load schedules');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSchedules();
  }, []);

  const handleToggleEnabled = async (schedule: Schedule) => {
    try {
      await apiService.updateSchedule(schedule.id, {
        enabled: !schedule.enabled
      });
      await fetchSchedules();
      toast.success(`Schedule ${!schedule.enabled ? 'enabled' : 'disabled'}`);
    } catch (error) {
      console.error('Failed to toggle schedule:', error);
      toast.error('Failed to update schedule');
    }
  };

  const handleDeleteSchedule = async (schedule: Schedule) => {
    setScheduleToDelete(schedule);
    setDeleteDialogOpen(true);
  };

  const confirmDeleteSchedule = async () => {
    if (!scheduleToDelete) return;

    try {
      setDeleting(true);
      await apiService.deleteSchedule(scheduleToDelete.id);
      await fetchSchedules();
      toast.success('Schedule deleted successfully');
    } catch (error) {
      console.error('Failed to delete schedule:', error);
      toast.error('Failed to delete schedule');
    } finally {
      setDeleting(false);
      setDeleteDialogOpen(false);
      setScheduleToDelete(null);
    }
  };

  const handleExecuteSchedule = async (schedule: Schedule) => {
    try {
      // Show initial start notification
      toast.success(
        `🚀 Starting schedule "${schedule.name}"`,
        {
          description: `Processing ${schedule.target_libraries.length || 'all'} libraries with ${schedule.badge_types.join(', ') || 'no'} badges`,
          duration: 3000
        }
      );

      const response = await apiService.executeSchedule(schedule.id);
      
      // Start polling for completion if we have an execution ID
      if (response.execution_id) {
        pollExecutionStatus(schedule, response.execution_id);
      }
    } catch (error) {
      console.error('Failed to execute schedule:', error);
      toast.error(
        `❌ Failed to start schedule "${schedule.name}"`,
        {
          description: 'Please check the logs for more details',
          duration: 5000
        }
      );
    }
  };

  const pollExecutionStatus = async (schedule: Schedule, executionId: string) => {
    const maxPolls = 60; // Poll for up to 5 minutes (60 * 5s = 5min)
    let pollCount = 0;

    const poll = async () => {
      try {
        const execution = await apiService.getScheduleExecution(schedule.id, executionId);
        
        if (execution.status === 'completed') {
          // Parse the items_processed JSON to get details
          let processedInfo = '';
          try {
            const processed = JSON.parse(execution.items_processed || '{}');
            processedInfo = `Processed ${processed.processed_items || 0} items${processed.failed_items ? ` (${processed.failed_items} failed)` : ''}`;
          } catch {
            processedInfo = 'Processing completed';
          }

          toast.success(
            `✅ Schedule "${schedule.name}" completed`,
            {
              description: processedInfo,
              duration: 5000
            }
          );
          return; // Stop polling
        } else if (execution.status === 'failed') {
          toast.error(
            `❌ Schedule "${schedule.name}" failed`,
            {
              description: execution.error_message || 'Check logs for details',
              duration: 7000
            }
          );
          return; // Stop polling
        } else if (execution.status === 'processing' && pollCount < maxPolls) {
          // Continue polling after 5 seconds
          pollCount++;
          setTimeout(poll, 5000);
        } else if (pollCount >= maxPolls) {
          // Timeout - stop polling but don't show error (execution might still be running)
          toast.info(
            `⏱️ Schedule "${schedule.name}" is still running`,
            {
              description: 'Check the schedule history for final status',
              duration: 4000
            }
          );
        }
      } catch (error) {
        console.error('Failed to check execution status:', error);
        // Don't show error toast for polling failures - just stop polling
      }
    };

    // Start the first poll after 2 seconds
    setTimeout(poll, 2000);
  };

  const formatCronExpression = (cron: string) => {
    // Simple cron expression formatting for display
    const presets: Record<string, string> = {
      '0 * * * *': 'Every hour',
      '0 2 * * *': 'Daily at 2:00 AM',
      '0 2 * * 0': 'Weekly (Sunday 2:00 AM)',
      '0 2 1 * *': 'Monthly (1st day 2:00 AM)',
      '0 */6 * * *': 'Every 6 hours',
      '0 2 * * 1-5': 'Weekdays at 2:00 AM',
      '0 2 * * 6,0': 'Weekends at 2:00 AM',
      '0 2,14 * * *': 'Twice daily (2:00 AM & 2:00 PM)'
    };
    
    return presets[cron] || cron;
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <h2 className="text-xl font-semibold">Active Schedules</h2>
          <Button onClick={onCreateSchedule} disabled>
            <Plus className="h-4 w-4 mr-2" />
            Create Schedule
          </Button>
        </div>
        <div className="text-center py-8">
          <Clock className="h-8 w-8 mx-auto mb-2 animate-spin" />
          <p>Loading schedules...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold">Active Schedules</h2>
        <Button onClick={onCreateSchedule}>
          <Plus className="h-4 w-4 mr-2" />
          Create Schedule
        </Button>
      </div>

      {schedules.length === 0 ? (
        <Card>
          <CardContent className="text-center py-8">
            <Clock className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
            <h3 className="text-lg font-medium mb-2">No schedules found</h3>
            <p className="text-muted-foreground mb-4">
              Create your first schedule to automate poster processing
            </p>
            <Button onClick={onCreateSchedule}>
              <Plus className="h-4 w-4 mr-2" />
              Create Schedule
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {schedules.map((schedule) => (
            <Card key={schedule.id}>
              <CardHeader>
                <div className="flex justify-between items-start">
                  <div>
                    <CardTitle className="flex items-center gap-2">
                      {schedule.name}
                      <Badge variant={schedule.enabled ? 'default' : 'secondary'}>
                        {schedule.enabled ? 'Enabled' : 'Disabled'}
                      </Badge>
                    </CardTitle>
                    <CardDescription>
                      {formatCronExpression(schedule.cron_expression)} • {schedule.timezone}
                    </CardDescription>
                  </div>
                  <div className="flex items-center gap-2">
                    <Switch
                      checked={schedule.enabled}
                      onCheckedChange={() => handleToggleEnabled(schedule)}
                    />
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleExecuteSchedule(schedule)}
                      disabled={!schedule.enabled}
                    >
                      <Play className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => onEditSchedule(schedule)}
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleDeleteSchedule(schedule)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-2">
                  <div>
                    <span className="text-sm font-medium">Badge Types: </span>
                    <span className="text-sm text-muted-foreground">
                      {schedule.badge_types.length > 0 ? schedule.badge_types.join(', ') : 'None'}
                    </span>
                  </div>
                  <div>
                    <span className="text-sm font-medium">Target Libraries: </span>
                    <span className="text-sm text-muted-foreground">
                      {schedule.target_libraries.length > 0 ? `${schedule.target_libraries.length} selected` : 'All libraries'}
                    </span>
                  </div>
                  <div>
                    <span className="text-sm font-medium">Reprocess All: </span>
                    <span className="text-sm text-muted-foreground">
                      {schedule.reprocess_all ? 'Yes' : 'No'}
                    </span>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Delete Schedule</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete "{scheduleToDelete?.name}"? This action cannot be undone.
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setDeleteDialogOpen(false);
                setScheduleToDelete(null);
              }}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={confirmDeleteSchedule}
              disabled={deleting}
            >
              {deleting ? (
                <>
                  <Clock className="h-4 w-4 mr-2 animate-spin" />
                  Deleting...
                </>
              ) : (
                'Delete Schedule'
              )}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
