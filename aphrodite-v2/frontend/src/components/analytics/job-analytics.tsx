'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  Clock, 
  TrendingUp, 
  Zap 
} from 'lucide-react';
import apiService from '@/services/api';
import { 
  JobStatusDistribution, 
  JobTypeDistribution 
} from '@/types/analytics';

export function JobAnalytics() {
  const [statusDistribution, setStatusDistribution] = useState<JobStatusDistribution[]>([]);
  const [typeDistribution, setTypeDistribution] = useState<JobTypeDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statusData, typeData] = await Promise.all([
          apiService.getJobStatusDistribution(),
          apiService.getJobTypeDistribution()
        ]);
        
        setStatusDistribution(statusData);
        setTypeDistribution(typeData);
      } catch (error) {
        console.error('Failed to fetch job analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'bg-green-500';
      case 'failed':
        return 'bg-red-500';
      case 'running':
        return 'bg-blue-500';
      case 'queued':
        return 'bg-yellow-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusBadgeVariant = (status: string): "default" | "secondary" | "destructive" | "outline" => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'default';
      case 'failed':
        return 'destructive';
      case 'running':
        return 'secondary';
      case 'queued':
        return 'outline';
      default:
        return 'secondary';
    }
  };

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

  if (loading) {
    return (
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {[...Array(2)].map((_, i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                <div className="h-32 bg-gray-200 rounded"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Job Status Distribution */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <BarChart3 className="h-5 w-5" />
            <span>Job Status Distribution</span>
          </CardTitle>
          <CardDescription>
            Breakdown of all jobs by their current status
          </CardDescription>
        </CardHeader>
        <CardContent>
          {statusDistribution.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No job data available
            </div>
          ) : (
            <div className="space-y-4">
              {statusDistribution.map((item, index) => (
                <div key={index} className="space-y-2">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                      <Badge variant={getStatusBadgeVariant(item.status)}>
                        {item.status}
                      </Badge>
                      <span className="text-sm font-medium">
                        {item.count} jobs
                      </span>
                    </div>
                    <span className="text-sm text-muted-foreground">
                      {item.percentage}%
                    </span>
                  </div>
                  <Progress 
                    value={item.percentage} 
                    className="h-2"
                  />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Job Type Performance */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Job Type Performance</span>
          </CardTitle>
          <CardDescription>
            Performance metrics by job type
          </CardDescription>
        </CardHeader>
        <CardContent>
          {typeDistribution.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No job type data available
            </div>
          ) : (
            <div className="space-y-4">
              {typeDistribution.map((item, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">{item.job_type}</h4>
                    <Badge variant="outline">
                      {item.count} jobs
                    </Badge>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div className="flex items-center space-x-2">
                      <TrendingUp className="h-4 w-4 text-green-600" />
                      <span>Success Rate: {item.success_rate}%</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Clock className="h-4 w-4 text-blue-600" />
                      <span>Avg Duration: {formatDuration(item.avg_duration_seconds)}</span>
                    </div>
                  </div>
                  
                  <Progress 
                    value={item.success_rate} 
                    className="h-2 mt-2"
                  />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
