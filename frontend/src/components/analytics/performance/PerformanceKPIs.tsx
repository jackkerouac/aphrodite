import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Timer, Target, Zap, Gauge, Activity } from 'lucide-react';
import type { PerformanceMetrics } from '../types';

interface PerformanceKPIsProps {
  metrics: PerformanceMetrics | null;
}

const formatDuration = (seconds: number | null) => {
  if (!seconds) return 'N/A';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
};

export function PerformanceKPIs({ metrics }: PerformanceKPIsProps) {
  if (!metrics) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <Activity className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>No performance data available</p>
            <p className="text-sm mt-2">Metrics will appear once jobs start processing.</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Average Duration</CardTitle>
          <Timer className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {formatDuration(metrics.avg_job_duration_seconds)}
          </div>
          <p className="text-xs text-muted-foreground">
            Per job completion
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Success Rate</CardTitle>
          <Target className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.success_rate_percentage.toFixed(1)}%</div>
          <p className="text-xs text-muted-foreground">
            {metrics.total_jobs_processed} jobs processed
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Throughput</CardTitle>
          <Zap className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">
            {metrics.average_throughput_posters_per_job.toFixed(1)}
          </div>
          <p className="text-xs text-muted-foreground">
            Posters per job
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Processing Rate</CardTitle>
          <Gauge className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">{metrics.jobs_per_hour_24h.toFixed(1)}</div>
          <p className="text-xs text-muted-foreground">
            Jobs per hour (24h)
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
