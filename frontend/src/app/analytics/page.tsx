'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { AnalyticsOverview } from '@/components/analytics/analytics-overview';
import { JobAnalytics } from '@/components/analytics/job-analytics';
import { ScheduleAnalytics } from '@/components/analytics/schedule-analytics';
import { SystemPerformance } from '@/components/analytics/system-performance';
import { Loader2, BarChart3, TrendingUp, Calendar, Activity } from 'lucide-react';
// import apiService from '@/services/api'; // Unused in current implementation
import { toast } from 'sonner';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const refreshData = async (silent = false) => {
    if (!silent) setRefreshing(true);
    
    try {
      setLastUpdated(new Date());
      if (!silent) {
        toast.success('Analytics data refreshed');
      }
    } catch (error) {
      console.error('Failed to refresh analytics:', error);
      toast.error('Failed to refresh analytics data');
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData(true);
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => refreshData(true), 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading analytics...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Analytics Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            System performance and processing insights
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <span className="text-sm text-muted-foreground">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          
          <button
            onClick={() => refreshData()}
            disabled={refreshing}
            className="flex items-center space-x-2 px-4 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 disabled:opacity-50"
          >
            {refreshing ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Activity className="h-4 w-4" />
            )}
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Overview Section */}
      <AnalyticsOverview />

      {/* Detailed Analytics Tabs */}
      <Tabs defaultValue="jobs" className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="jobs" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Job Analytics</span>
          </TabsTrigger>
          <TabsTrigger value="schedules" className="flex items-center space-x-2">
            <Calendar className="h-4 w-4" />
            <span>Schedules</span>
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4" />
            <span>Performance</span>
          </TabsTrigger>
          <TabsTrigger value="trends" className="flex items-center space-x-2">
            <Activity className="h-4 w-4" />
            <span>Trends</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="jobs" className="space-y-6">
          <JobAnalytics />
        </TabsContent>

        <TabsContent value="schedules" className="space-y-6">
          <ScheduleAnalytics />
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <SystemPerformance />
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Processing Trends</CardTitle>
              <CardDescription>
                Historical view of processing activity and patterns
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="text-center text-muted-foreground py-8">
                Processing trends chart will be displayed here
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
