'use client';

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Activity, Image, Clock, CheckCircle, Database, Loader2 } from 'lucide-react';
import { useDashboardData } from '@/hooks/useDashboardData';

export default function Dashboard() {
  const { systemStatus, stats, recentJobs, isLoading, error, version } = useDashboardData();

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
          <p className="text-muted-foreground">
            Welcome to Aphrodite v2 - Your media poster enhancement system
          </p>
        </div>
        <Card>
          <CardContent className="flex items-center justify-center p-6">
            <div className="text-center">
              <p className="text-destructive mb-2">Error loading dashboard data</p>
              <p className="text-sm text-muted-foreground">{error}</p>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
        <p className="text-muted-foreground">
          Welcome to Aphrodite v2 - Your media poster enhancement system
        </p>
      </div>

      {/* System Status Cards */}
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">API Status</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              {isLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Badge 
                  variant="outline" 
                  className={systemStatus.api_status === 'online' 
                    ? "text-green-600 border-green-600" 
                    : "text-red-600 border-red-600"
                  }
                >
                  {systemStatus.api_status === 'online' ? 'Online' : 'Offline'}
                </Badge>
              )}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Backend services {systemStatus.api_status}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Media Items</CardTitle>
            <Image className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                stats.total_media_items.toLocaleString()
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Total items in library
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Jobs</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                stats.active_jobs
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Currently processing
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Completed Today</CardTitle>
            <CheckCircle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {isLoading ? (
                <Loader2 className="h-6 w-6 animate-spin" />
              ) : (
                stats.completed_today
              )}
            </div>
            <p className="text-xs text-muted-foreground">
              Posters enhanced
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Current Jobs and System Information */}
      <div className="grid gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>
              Latest job processing activity
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {isLoading ? (
              <div className="flex items-center justify-center p-6">
                <Loader2 className="h-6 w-6 animate-spin" />
              </div>
            ) : recentJobs.length > 0 ? (
              recentJobs.map((job) => (
                <div key={job.id} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium">{job.name}</span>
                    <Badge 
                      variant={
                        job.status === 'completed' ? 'default' :
                        job.status === 'running' ? 'secondary' :
                        job.status === 'failed' ? 'destructive' : 'outline'
                      }
                      className={
                        job.status === 'completed' ? 'bg-green-600' : ''
                      }
                    >
                      {job.status.charAt(0).toUpperCase() + job.status.slice(1)}
                    </Badge>
                  </div>
                  <Progress value={job.progress} className="h-2" />
                  <p className="text-xs text-muted-foreground">
                    {job.status === 'completed' 
                      ? 'Completed' 
                      : job.status === 'failed'
                      ? 'Failed'
                      : job.status === 'running'
                      ? `${job.progress}% complete`
                      : 'Waiting to start'
                    }
                  </p>
                </div>
              ))
            ) : (
              <div className="text-center py-6">
                <p className="text-sm text-muted-foreground">No recent jobs</p>
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>System Information</CardTitle>
            <CardDescription>
              Current system status and configuration
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <p className="font-medium">Version</p>
                <p className="text-muted-foreground">{isLoading ? '...' : version}</p>
              </div>
              <div>
                <p className="font-medium">Jellyfin Status</p>
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Badge 
                    variant="outline" 
                    className={systemStatus.jellyfin_status === 'connected'
                      ? "text-green-600 border-green-600"
                      : "text-red-600 border-red-600"
                    }
                  >
                    {systemStatus.jellyfin_status === 'connected' ? 'Connected' : 'Disconnected'}
                  </Badge>
                )}
              </div>
              <div>
                <p className="font-medium">Database</p>
                <div className="flex items-center gap-2">
                  <Database className="h-3 w-3" />
                  <span className="text-muted-foreground">PostgreSQL</span>
                  {isLoading ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <div className={`h-2 w-2 rounded-full ${
                      systemStatus.database_status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                  )}
                </div>
              </div>
              <div>
                <p className="font-medium">Queue</p>
                <div className="flex items-center gap-2">
                  <span className="text-muted-foreground">Redis</span>
                  {isLoading ? (
                    <Loader2 className="h-3 w-3 animate-spin" />
                  ) : (
                    <div className={`h-2 w-2 rounded-full ${
                      systemStatus.queue_status === 'healthy' ? 'bg-green-500' : 'bg-red-500'
                    }`} />
                  )}
                </div>
              </div>
              <div>
                <p className="font-medium">Workers</p>
                <p className="text-muted-foreground">{systemStatus.workers_active} active</p>
              </div>
              <div>
                <p className="font-medium">Success Rate</p>
                <p className="text-muted-foreground">
                  {isLoading ? '...' : `${stats.processing_success_rate}%`}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
