'use client';

import { useState, useEffect } from 'react';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Button } from '@/components/ui/button';
import { Loader2, Search, Activity, Users, BarChart3, TrendingUp } from 'lucide-react';
import apiService from '@/services/api';
import { toast } from 'sonner';

import { OverviewTab } from '@/components/analytics/OverviewTab';
import { SearchTab } from '@/components/analytics/SearchTab';
import { UsersTab } from '@/components/analytics/UsersTab';
import { PerformanceTab } from '@/components/analytics/PerformanceTab';
import type { SystemOverview, ActivitySearchParams, SearchResult } from '@/components/analytics/types';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [systemOverview, setSystemOverview] = useState<SystemOverview | null>(null);
  const [searchParams, setSearchParams] = useState<ActivitySearchParams>({
    limit: 50,
    offset: 0,
    sort_by: 'created_at',
    sort_order: 'desc',
    include_details: false
  });
  const [searchResults, setSearchResults] = useState<SearchResult | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [suggestions, setSuggestions] = useState<any>(null);
  const [activeTab, setActiveTab] = useState('overview');

  const refreshData = async (silent = false) => {
    if (!silent) setRefreshing(true);
    
    try {
      // Get system overview
      const overviewData = await apiService.getSystemAnalyticsOverview(7);
      if (overviewData.success) {
        setSystemOverview(overviewData.data);
      }
      
      // Get search suggestions for filters
      const suggestionsData = await apiService.getSearchSuggestions();
      if (suggestionsData.success) {
        setSuggestions(suggestionsData.suggestions);
      }
      
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

  const performSearch = async () => {
    setSearchLoading(true);
    try {
      const result = await apiService.advancedActivitySearch(searchParams);
      if (result.success) {
        setSearchResults(result.data);
      } else {
        toast.error('Search failed: ' + result.error);
      }
    } catch (error) {
      console.error('Search failed:', error);
      toast.error('Search failed');
    } finally {
      setSearchLoading(false);
    }
  };

  useEffect(() => {
    refreshData(true);
    
    // Auto-refresh every 5 minutes
    const interval = setInterval(() => refreshData(true), 5 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (activeTab === 'search' && !searchResults) {
      performSearch();
    }
  }, [activeTab]);

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
          <h1 className="text-3xl font-bold tracking-tight">Activity Tracking Analytics</h1>
          <p className="text-muted-foreground mt-2">
            Comprehensive insights into system activity, performance, and user patterns
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <span className="text-sm text-muted-foreground">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          
          <Button
            onClick={() => refreshData()}
            disabled={refreshing}
            variant="outline"
          >
            {refreshing ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <Activity className="h-4 w-4 mr-2" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Overview</span>
          </TabsTrigger>
          <TabsTrigger value="search" className="flex items-center space-x-2">
            <Search className="h-4 w-4" />
            <span>Advanced Search</span>
          </TabsTrigger>
          <TabsTrigger value="users" className="flex items-center space-x-2">
            <Users className="h-4 w-4" />
            <span>User Analytics</span>
          </TabsTrigger>
          <TabsTrigger value="performance" className="flex items-center space-x-2">
            <TrendingUp className="h-4 w-4" />
            <span>Performance</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          {systemOverview && (
            <OverviewTab systemOverview={systemOverview} />
          )}
        </TabsContent>

        <TabsContent value="search" className="space-y-6">
          <SearchTab
            searchParams={searchParams}
            setSearchParams={setSearchParams}
            searchResults={searchResults}
            searchLoading={searchLoading}
            suggestions={suggestions}
            onSearch={performSearch}
          />
        </TabsContent>

        <TabsContent value="users" className="space-y-6">
          <UsersTab />
        </TabsContent>

        <TabsContent value="performance" className="space-y-6">
          <PerformanceTab />
        </TabsContent>
      </Tabs>
    </div>
  );
}
