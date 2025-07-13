import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Clock, Zap } from 'lucide-react';
import type { PerformanceMetrics } from '../types';

interface PerformanceDetailsProps {
  metrics: PerformanceMetrics | null;
}

const formatDuration = (seconds: number | null) => {
  if (!seconds) return 'N/A';
  if (seconds < 60) return `${seconds.toFixed(1)}s`;
  if (seconds < 3600) return `${(seconds / 60).toFixed(1)}m`;
  return `${(seconds / 3600).toFixed(1)}h`;
};

const formatDate = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

const getEfficiencyBadgeVariant = (score: number) => {
  if (score >= 2) return 'default';
  if (score >= 1) return 'secondary';
  return 'outline';
};

export function PerformanceDetails({ metrics }: PerformanceDetailsProps) {
  if (!metrics) {
    return null;
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Processing Efficiency */}
      <Card>
        <CardHeader>
          <CardTitle>Processing Efficiency</CardTitle>
          <CardDescription>
            Job duration analysis and performance variance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Fastest Job</span>
              <span className="text-sm text-green-600">
                {formatDuration(metrics.processing_efficiency.fastest_job_duration)}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Slowest Job</span>
              <span className="text-sm text-red-600">
                {formatDuration(metrics.processing_efficiency.slowest_job_duration)}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Median Duration</span>
              <span className="text-sm">
                {formatDuration(metrics.processing_efficiency.median_duration)}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">Performance Variance</span>
              <span className="text-sm">
                {formatDuration(metrics.processing_efficiency.efficiency_variance)}
              </span>
            </div>
            
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">High Throughput Jobs</span>
              <Badge variant="secondary">
                {metrics.processing_efficiency.high_throughput_jobs}
              </Badge>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Peak Processing Times */}
      <Card>
        <CardHeader>
          <CardTitle>Peak Processing Times</CardTitle>
          <CardDescription>
            Hours with highest processing activity
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {metrics.peak_processing_times.length === 0 ? (
              <div className="text-center text-muted-foreground py-4">
                <Clock className="h-8 w-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No peak times data available</p>
              </div>
            ) : (
              metrics.peak_processing_times.map((peak, index) => (
                <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                  <div className="flex flex-col">
                    <span className="font-medium">
                      {formatDate(peak.hour)}
                    </span>
                    <span className="text-xs text-muted-foreground">
                      {peak.jobs_count} jobs • {peak.total_posters} posters
                    </span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Badge variant={getEfficiencyBadgeVariant(peak.efficiency_score)}>
                      <Zap className="h-3 w-3 mr-1" />
                      {peak.efficiency_score.toFixed(1)}
                    </Badge>
                    <span className="text-xs text-muted-foreground">
                      {formatDuration(peak.avg_duration_seconds)}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
          
          {metrics.peak_processing_times.length > 0 && (
            <div className="mt-4 p-3 bg-muted rounded-lg">
              <div className="text-sm text-muted-foreground">
                <strong>Peak Performance:</strong> Efficiency score measures posters processed per second
              </div>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
