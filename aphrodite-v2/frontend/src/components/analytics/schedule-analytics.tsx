'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { 
  Calendar, 
  Clock, 
  CheckCircle, 
  XCircle, 
  Tag,
  Database
} from 'lucide-react';
import apiService from '@/services/api';
import { ScheduleAnalytics as ScheduleAnalyticsType } from '@/types/analytics';

export function ScheduleAnalytics() {
  const [schedules, setSchedules] = useState<ScheduleAnalyticsType[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await apiService.getScheduleAnalytics();
        setSchedules(data);
      } catch (error) {
        console.error('Failed to fetch schedule analytics:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const formatLastExecution = (lastExecution: string | null) => {
    if (!lastExecution) return 'Never executed';
    
    const date = new Date(lastExecution);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffMinutes = Math.floor(diffMs / (1000 * 60));
    
    if (diffDays > 0) {
      return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
    } else if (diffHours > 0) {
      return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    } else if (diffMinutes > 0) {
      return `${diffMinutes} minute${diffMinutes > 1 ? 's' : ''} ago`;
    } else {
      return 'Just now';
    }
  };

  const getBadgeTypeColor = (badgeType: string) => {
    switch (badgeType.toLowerCase()) {
      case 'resolution':
        return 'bg-blue-100 text-blue-800';
      case 'review':
        return 'bg-green-100 text-green-800';
      case 'awards':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="space-y-6">
        <Card>
          <CardContent className="pt-6">
            <div className="animate-pulse space-y-4">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-32 bg-gray-200 rounded"></div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  const enabledSchedules = schedules.filter(s => s.enabled);
  const disabledSchedules = schedules.filter(s => !s.enabled);
  const averageSuccessRate = schedules.length > 0 
    ? schedules.reduce((sum, s) => sum + s.success_rate, 0) / schedules.length 
    : 0;

  return (
    <div className="space-y-6">
      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Schedules</p>
                <p className="text-2xl font-bold">{schedules.length}</p>
              </div>
              <Calendar className="h-8 w-8 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Enabled Schedules</p>
                <p className="text-2xl font-bold">{enabledSchedules.length}</p>
              </div>
              <CheckCircle className="h-8 w-8 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="pt-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Average Success Rate</p>
                <p className="text-2xl font-bold">{averageSuccessRate.toFixed(1)}%</p>
              </div>
              <CheckCircle className="h-8 w-8 text-emerald-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Schedules List */}
      <Card>
        <CardHeader>
          <CardTitle>Schedule Details</CardTitle>
          <CardDescription>
            Detailed information about each schedule and its performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          {schedules.length === 0 ? (
            <div className="text-center text-muted-foreground py-8">
              No schedules configured
            </div>
          ) : (
            <div className="space-y-4">
              {schedules.map((schedule) => (
                <div key={schedule.id} className="border rounded-lg p-4">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <h4 className="font-medium">{schedule.name}</h4>
                        <Badge variant={schedule.enabled ? "default" : "secondary"}>
                          {schedule.enabled ? "Enabled" : "Disabled"}
                        </Badge>
                      </div>
                      
                      <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-2">
                        <div className="flex items-center space-x-1">
                          <Clock className="h-4 w-4" />
                          <span>{formatLastExecution(schedule.last_execution)}</span>
                        </div>
                        <div className="flex items-center space-x-1">
                          <Database className="h-4 w-4" />
                          <span>{schedule.execution_count} executions</span>
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2 mb-3">
                        {schedule.badge_types.map((badgeType, index) => (
                          <span
                            key={index}
                            className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getBadgeTypeColor(badgeType)}`}
                          >
                            <Tag className="h-3 w-3 mr-1" />
                            {badgeType}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div className="text-right">
                      <div className="text-2xl font-bold">
                        {schedule.success_rate.toFixed(1)}%
                      </div>
                      <div className="text-sm text-muted-foreground">
                        Success Rate
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <Progress value={schedule.success_rate} className="h-2" />
                    
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>{schedule.target_libraries.length} target libraries</span>
                      <span>
                        {schedule.execution_count > 0 
                          ? `${Math.round(schedule.success_rate * schedule.execution_count / 100)} successful`
                          : 'No executions yet'
                        }
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
