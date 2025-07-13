import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Activity, Users, BarChart3, CheckCircle, ExternalLink } from 'lucide-react';
import { ActivityDetailsDialog } from './dialogs';
import type { SystemOverview } from './types';

interface OverviewTabProps {
  systemOverview: SystemOverview;
}



const formatDuration = (ms: number | null) => {
  if (!ms) return 'N/A';
  if (ms < 1000) return `${ms}ms`;
  if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
  return `${(ms / 60000).toFixed(1)}m`;
};

const formatDate = (dateString: string | null) => {
  if (!dateString) return 'N/A';
  return new Date(dateString).toLocaleString();
};

export function OverviewTab({ systemOverview }: OverviewTabProps) {
  const [selectedActivityType, setSelectedActivityType] = useState<string | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);

  const handleActivityTypeClick = (activityType: string) => {
    setSelectedActivityType(activityType);
    setDialogOpen(true);
  };

  const getActivityTypeName = (activityType: string) => {
    switch (activityType) {
      case 'badge_application':
        return 'Badge Application';
      case 'poster_replacement':
        return 'Poster Replacement';
      default:
        return activityType.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
  };

  return (
    <>
    <div className="space-y-6">
      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Activities</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemOverview.summary.total_activities.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              Last {systemOverview.analysis_period.days} days
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemOverview.summary.success_rate.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              {systemOverview.overall_statistics.totals.successful.toLocaleString()} successful
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Users</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemOverview.summary.active_users}</div>
            <p className="text-xs text-muted-foreground">
              Unique users with activity
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Batch Jobs</CardTitle>
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemOverview.summary.active_batches}</div>
            <p className="text-xs text-muted-foreground">
              Recent batch operations
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Activity Type Breakdown and Recent Batches */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Activity Type Breakdown</CardTitle>
            <CardDescription>
              Distribution of activity types and their success rates
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {systemOverview.overall_statistics.activity_type_breakdown.map((type) => (
                <div key={type.activity_type} className="group">
                  <Button
                    variant="ghost"
                    className="w-full p-3 h-auto justify-between hover:bg-muted/50"
                    onClick={() => handleActivityTypeClick(type.activity_type)}
                  >
                    <div className="flex flex-col items-start">
                      <span className="font-medium capitalize">
                        {type.activity_type.replace('_', ' ')}
                      </span>
                      <span className="text-sm text-muted-foreground">
                        {type.total.toLocaleString()} total
                      </span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Badge
                        variant={type.success_rate >= 90 ? 'default' : type.success_rate >= 70 ? 'secondary' : 'destructive'}
                      >
                        {type.success_rate.toFixed(1)}%
                      </Badge>
                      <div className="flex space-x-1">
                        <span className="text-xs text-green-600">{type.successful}</span>
                        <span className="text-xs text-muted-foreground">/</span>
                        <span className="text-xs text-red-600">{type.failed}</span>
                      </div>
                      <ExternalLink className="h-4 w-4 opacity-0 group-hover:opacity-100 transition-opacity" />
                    </div>
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Recent Batch Jobs</CardTitle>
            <CardDescription>
              Latest batch operations and their status
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {systemOverview.recent_batches.batches.slice(0, 5).map((batch) => (
                <div key={batch.batch_job_id} className="flex items-center justify-between">
                  <div className="flex flex-col">
                    <span className="font-mono text-sm">
                      {batch.batch_job_id.substring(0, 8)}...
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {formatDate(batch.start_time)}
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge
                      variant={batch.success_rate >= 90 ? 'default' : batch.success_rate >= 70 ? 'secondary' : 'destructive'}
                    >
                      {batch.success_rate.toFixed(1)}%
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {batch.total_activities} items
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {formatDuration(batch.batch_duration_ms)}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Top Users */}
      <Card>
        <CardHeader>
          <CardTitle>Most Active Users</CardTitle>
          <CardDescription>
            Users with the highest activity in the last {systemOverview.analysis_period.days} days
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {systemOverview.top_users.users.map((user) => (
              <div key={user.user_id} className="p-4 border rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium truncate">{user.user_id}</span>
                  <Badge
                    variant={user.success_rate >= 90 ? 'default' : user.success_rate >= 70 ? 'secondary' : 'destructive'}
                  >
                    {user.success_rate.toFixed(1)}%
                  </Badge>
                </div>
                <div className="text-sm text-muted-foreground">
                  {user.total_activities.toLocaleString()} activities
                </div>
                <div className="flex justify-between text-xs mt-1">
                  <span className="text-green-600">{user.successful} successful</span>
                  <span className="text-red-600">{user.failed} failed</span>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>

    {/* Activity Details Dialog */}
    {selectedActivityType && (
      <ActivityDetailsDialog
        open={dialogOpen}
        onOpenChange={setDialogOpen}
        activityType={selectedActivityType}
        activityTypeName={getActivityTypeName(selectedActivityType)}
      />
    )}
    </>
  );
}
