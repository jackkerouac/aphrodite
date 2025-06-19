'use client';

import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Separator } from '@/components/ui/separator';
import { Play, Square, Trash2, Download, Upload, Settings, AlertTriangle } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { ProcessingJob } from './types';

interface ProcessingControlsProps {
  jobs: ProcessingJob[];
  loading: boolean;
  onAddJob?: (mediaIds: string[], badgeTypes: string[]) => Promise<boolean>;
  onCancelJob?: (jobId: string) => Promise<boolean>;
  onLoadJobs?: () => void;
  selectedMedia?: string;
  selectedBadgeTypes: string[];
  className?: string;
}

export function ProcessingControls({
  jobs,
  loading,
  onAddJob,
  onCancelJob,
  onLoadJobs,
  selectedMedia,
  selectedBadgeTypes,
  className = ''
}: ProcessingControlsProps) {
  const activeJobs = jobs.filter(job => job.status === 'running');
  const pendingJobs = jobs.filter(job => job.status === 'pending');
  const completedJobs = jobs.filter(job => job.status === 'completed');
  const failedJobs = jobs.filter(job => job.status === 'failed');

  const handleApplyChanges = async () => {
    if (!selectedMedia || selectedBadgeTypes.length === 0 || !onAddJob) return;
    
    await onAddJob([selectedMedia], selectedBadgeTypes);
  };

  const handleBatchProcess = async () => {
    if (selectedBadgeTypes.length === 0 || !onAddJob) return;
    
    // TODO: Implement batch processing with multiple selected items
    console.log('Batch processing not yet implemented');
  };

  const formatJobType = (type: string) => {
    const typeMap: Record<string, string> = {
      'preview': 'Preview',
      'apply': 'Apply Changes',
      'batch': 'Batch Processing',
      'badge_processing': 'Badge Processing'
    };
    return typeMap[type] || type;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-500';
      case 'running':
        return 'bg-blue-500';
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Play className="h-5 w-5" />
          Processing Controls
        </CardTitle>
        <CardDescription>
          Apply changes to Jellyfin and manage processing queue (coming soon)
        </CardDescription>
      </CardHeader>
      
      <CardContent className="space-y-6">
        {/* Feature Notice */}
        <Alert>
          <AlertTriangle className="h-4 w-4" />
          <AlertDescription>
            Processing controls are coming in a future update. Currently focused on preview functionality.
          </AlertDescription>
        </Alert>

        {/* Quick Actions */}
        <div className="space-y-3">
          <h4 className="text-sm font-medium">Quick Actions</h4>
          
          <div className="grid grid-cols-2 gap-2">
            <Button
              variant="outline"
              onClick={handleApplyChanges}
              disabled={!selectedMedia || selectedBadgeTypes.length === 0}
              className="h-auto py-3 flex-col gap-1"
            >
              <Upload className="h-4 w-4" />
              <span className="text-xs">Apply to Selected</span>
            </Button>
            
            <Button
              variant="outline"
              onClick={handleBatchProcess}
              disabled={selectedBadgeTypes.length === 0}
              className="h-auto py-3 flex-col gap-1"
            >
              <Settings className="h-4 w-4" />
              <span className="text-xs">Batch Process</span>
            </Button>
          </div>
        </div>

        <Separator />

        {/* Queue Status */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <h4 className="text-sm font-medium">Queue Status</h4>
            <Button
              variant="ghost"
              size="sm"
              onClick={onLoadJobs}
              disabled={loading}
            >
              {loading ? (
                <div className="h-4 w-4 animate-spin rounded-full border-2 border-background border-t-foreground" />
              ) : (
                'Refresh'
              )}
            </Button>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="space-y-1">
              <div className="text-2xl font-bold text-blue-600">{activeJobs.length}</div>
              <div className="text-xs text-muted-foreground">Active</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-yellow-600">{pendingJobs.length}</div>
              <div className="text-xs text-muted-foreground">Pending</div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-center">
            <div className="space-y-1">
              <div className="text-2xl font-bold text-green-600">{completedJobs.length}</div>
              <div className="text-xs text-muted-foreground">Completed</div>
            </div>
            <div className="space-y-1">
              <div className="text-2xl font-bold text-red-600">{failedJobs.length}</div>
              <div className="text-xs text-muted-foreground">Failed</div>
            </div>
          </div>
        </div>

        {/* Active Jobs */}
        {activeJobs.length > 0 && (
          <>
            <Separator />
            <div className="space-y-3">
              <h4 className="text-sm font-medium">Active Jobs</h4>
              <div className="space-y-2">
                {activeJobs.map((job) => (
                  <div key={job.id} className="p-3 border rounded-lg space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(job.status)}`} />
                        <span className="text-sm font-medium">
                          {formatJobType(job.type)}
                        </span>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => onCancelJob?.(job.id)}
                      >
                        <Square className="h-4 w-4" />
                      </Button>
                    </div>
                    
                    <Progress value={job.progress} className="h-1" />
                    
                    <div className="flex items-center justify-between text-xs text-muted-foreground">
                      <span>{job.progress}% complete</span>
                      <span>{job.media_ids.length} items</span>
                    </div>
                    
                    <div className="flex flex-wrap gap-1">
                      {job.badge_types.map((badgeType) => (
                        <Badge key={badgeType} variant="secondary" className="text-xs">
                          {badgeType}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </>
        )}

        {/* Recent Jobs */}
        {(completedJobs.length > 0 || failedJobs.length > 0) && (
          <>
            <Separator />
            <div className="space-y-3">
              <h4 className="text-sm font-medium">Recent Jobs</h4>
              <div className="space-y-2 max-h-32 overflow-y-auto">
                {[...completedJobs, ...failedJobs]
                  .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
                  .slice(0, 5)
                  .map((job) => (
                    <div key={job.id} className="flex items-center justify-between p-2 border rounded text-sm">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${getStatusColor(job.status)}`} />
                        <span>{formatJobType(job.type)}</span>
                        <Badge variant="outline" className="text-xs">
                          {job.media_ids.length} items
                        </Badge>
                      </div>
                      <div className="flex items-center gap-2">
                        {job.status === 'completed' && (
                          <Button variant="ghost" size="sm">
                            <Download className="h-4 w-4" />
                          </Button>
                        )}
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => onCancelJob?.(job.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  ))}
              </div>
            </div>
          </>
        )}

        {/* Empty State */}
        {jobs.length === 0 && !loading && (
          <div className="text-center py-8 text-sm text-muted-foreground">
            No processing jobs found
          </div>
        )}
      </CardContent>
    </Card>
  );
}
