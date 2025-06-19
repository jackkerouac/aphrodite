'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  Activity, 
  Clock, 
  TrendingUp, 
  Zap,
  AlertTriangle,
  CheckCircle
} from 'lucide-react';
import apiService from '@/services/api';
import { SystemPerformance as SystemPerformanceType } from '@/types/analytics';

export function SystemPerformance() {
  const [performance, setPerformance] = useState<SystemPerformanceType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiService.getSystemPerformance();
        setPerformance(data);
      } catch (error) {
        console.error('Failed to fetch system performance:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatDuration = (seconds: number | null) => {
    if (!seconds) return 'N/A';
    
    if (seconds < 60) {
      return `${seconds.toFixed(1)}s`;
    } else if (seconds < 3600) {
      return `${(seconds / 60).toFixed(1)}m`;
    } else {
      return `${(seconds / 3600).toFixed(1)}h`;
    }
  };

  const getHealthStatusColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getHealthStatusIcon = (score: number) => {
    if (score >= 80) return <CheckCircle className="h-5 w-5 text-green-600" />;
    if (score >= 60) return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
    return <AlertTriangle className="h-5 w-5 text-red-600" />;
  };

  const getHealthStatusText = (score: number) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    return 'Poor';
  };

  const formatHour = (hour: number) => {
    const date = new Date();
    date.setHours(hour, 0, 0, 0);
    return date.toLocaleTimeString('en-US', { 
      hour: 'numeric', 
      hour12: true 
    });
  };

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(4)].map((_, i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-16 bg-gray-200 rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (!performance) {
    return (
      <div className="text-center text-muted-foreground py-8">
        Failed to load performance data
      </div>
    );
  }

  const performanceMetrics = [
    {
      title: 'Average Job Duration',
      value: formatDuration(performance.avg_job_duration_seconds),
      icon: Clock,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
      description: 'Time taken to complete jobs on average'
    },
    {
      title: 'Jobs per Hour (24h)',
      value: performance.jobs_per_hour_24h.toFixed(1),
      icon: Activity,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
      description: 'Processing rate over the last 24 hours'
    },
    {
      title: 'Peak Hour Activity',
      value: `${performance.peak_hour_jobs} jobs`,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
      description: `Highest activity at ${formatHour(performance.peak_hour)}`
    },
    {
      title: 'Queue Health Score',
      value: `${performance.queue_health_score.toFixed(1)}%`,
      icon: Zap,
      color: getHealthStatusColor(performance.queue_health_score),
      bgColor: performance.queue_health_score >= 80 ? 'bg-green-100' : 
                performance.queue_health_score >= 60 ? 'bg-yellow-100' : 'bg-red-100',
      description: 'Overall system health indicator'
    }
  ];

  return (
    <div className="space-y-6">
      {/* Performance Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {performanceMetrics.map((metric, index) => {
          const Icon = metric.icon;
          return (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between mb-2">
                  <div className={`p-2 rounded-full ${metric.bgColor}`}>
                    <Icon className={`h-6 w-6 ${metric.color}`} />
                  </div>
                </div>
                
                <div className="space-y-1">
                  <p className="text-sm font-medium text-muted-foreground">
                    {metric.title}
                  </p>
                  <p className="text-2xl font-bold">{metric.value}</p>
                  <p className="text-xs text-muted-foreground">
                    {metric.description}
                  </p>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Detailed Performance Analysis */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* System Health Card */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              {getHealthStatusIcon(performance.queue_health_score)}
              <span>System Health</span>
            </CardTitle>
            <CardDescription>
              Overall system performance and queue health
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-lg font-medium">
                  {getHealthStatusText(performance.queue_health_score)}
                </span>
                <Badge 
                  variant={performance.queue_health_score >= 80 ? "default" : 
                           performance.queue_health_score >= 60 ? "secondary" : "destructive"}
                >
                  {performance.queue_health_score.toFixed(1)}%
                </Badge>
              </div>
              
              <Progress 
                value={performance.queue_health_score} 
                className="h-3"
              />
              
              <div className="text-sm text-muted-foreground space-y-1">
                <p>
                  The health score is calculated based on queue size and failure rates.
                </p>
                <p>
                  • <strong>80-100%:</strong> Excellent performance
                </p>
                <p>
                  • <strong>60-79%:</strong> Good performance
                </p>
                <p>
                  • <strong>40-59%:</strong> Fair performance, may need attention
                </p>
                <p>
                  • <strong>0-39%:</strong> Poor performance, requires immediate attention
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Activity Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <Activity className="h-5 w-5" />
              <span>Activity Insights</span>
            </CardTitle>
            <CardDescription>
              Processing patterns and peak usage times
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-green-600">
                    {performance.jobs_per_hour_24h.toFixed(1)}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Jobs/Hour (24h avg)
                  </div>
                </div>
                
                <div className="text-center p-4 border rounded-lg">
                  <div className="text-2xl font-bold text-purple-600">
                    {performance.peak_hour_jobs}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    Peak Hour Jobs
                  </div>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Peak Activity Time</span>
                  <span className="text-sm text-muted-foreground">
                    {formatHour(performance.peak_hour)}
                  </span>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm font-medium">Average Processing Time</span>
                  <span className="text-sm text-muted-foreground">
                    {formatDuration(performance.avg_job_duration_seconds)}
                  </span>
                </div>
              </div>

              <div className="text-xs text-muted-foreground mt-4">
                <p>
                  <strong>Tip:</strong> Consider scheduling heavy processing tasks 
                  during off-peak hours to optimize system performance.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
