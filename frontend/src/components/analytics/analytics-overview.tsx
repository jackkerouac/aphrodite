'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { 
  CheckCircle, 
  XCircle, 
  Clock, 
  Play, 
  Calendar, 
  Users, 
  Database,
  TrendingUp 
} from 'lucide-react';
import apiService from '@/services/api';
import { AnalyticsOverview as AnalyticsOverviewType } from '@/types/analytics';

export function AnalyticsOverview() {
  const [overview, setOverview] = useState<AnalyticsOverviewType | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchOverview = async () => {
      try {
        const data = await apiService.getAnalyticsOverview();
        setOverview(data);
      } catch (error) {
        console.error('Failed to fetch analytics overview:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchOverview();
  }, []);

  if (loading || !overview) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[...Array(8)].map((_, i) => (
          <Card key={i}>
            <CardContent className="pt-6">
              <div className="animate-pulse">
                <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-1/2"></div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const stats = [
    {
      title: 'Total Jobs',
      value: overview.total_jobs,
      icon: Database,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Completed Jobs',
      value: overview.completed_jobs,
      icon: CheckCircle,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Failed Jobs',
      value: overview.failed_jobs,
      icon: XCircle,
      color: 'text-red-600',
      bgColor: 'bg-red-100',
    },
    {
      title: 'Queued Jobs',
      value: overview.queued_jobs,
      icon: Clock,
      color: 'text-yellow-600',
      bgColor: 'bg-yellow-100',
    },
    {
      title: 'Running Jobs',
      value: overview.running_jobs,
      icon: Play,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Total Schedules',
      value: overview.total_schedules,
      icon: Calendar,
      color: 'text-indigo-600',
      bgColor: 'bg-indigo-100',
    },
    {
      title: 'Active Schedules',
      value: overview.active_schedules,
      icon: Users,
      color: 'text-teal-600',
      bgColor: 'bg-teal-100',
    },
    {
      title: 'Media Items',
      value: overview.total_media_items,
      icon: Database,
      color: 'text-gray-600',
      bgColor: 'bg-gray-100',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Key Metrics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <Card key={index}>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-muted-foreground">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold">{stat.value.toLocaleString()}</p>
                  </div>
                  <div className={`p-2 rounded-full ${stat.bgColor}`}>
                    <Icon className={`h-6 w-6 ${stat.color}`} />
                  </div>
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Success Rate Card */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <TrendingUp className="h-5 w-5" />
            <span>Processing Success Rate</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-2xl font-bold">
                {overview.processing_success_rate}%
              </span>
              <span className="text-sm text-muted-foreground">
                {overview.completed_jobs} of {overview.completed_jobs + overview.failed_jobs} processed jobs
              </span>
            </div>
            
            <Progress 
              value={overview.processing_success_rate} 
              className="h-2"
            />
            
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div className="flex items-center space-x-2">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span>Successful: {overview.completed_jobs}</span>
              </div>
              <div className="flex items-center space-x-2">
                <XCircle className="h-4 w-4 text-red-600" />
                <span>Failed: {overview.failed_jobs}</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
