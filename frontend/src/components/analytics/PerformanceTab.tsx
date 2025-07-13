import { useState, useEffect } from 'react';
import { Loader2, RefreshCw } from 'lucide-react';
import { Button } from '@/components/ui/button';
import apiService from '@/services/api';
import { toast } from 'sonner';
import type { PerformanceMetrics } from '../types';

import { PerformanceKPIs, PerformanceCharts, PerformanceDetails } from './performance';

export function PerformanceTab() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetchMetrics = async (silent = false) => {
    if (!silent) setRefreshing(true);
    
    try {
      const response = await apiService.getPerformanceMetrics();
      if (response) {
        setMetrics(response);
        setLastUpdated(new Date());
        if (!silent) {
          toast.success('Performance metrics updated');
        }
      }
    } catch (error) {
      console.error('Failed to fetch performance metrics:', error);
      toast.error('Failed to load performance metrics');
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics(true);
    
    // Auto-refresh every 2 minutes
    const interval = setInterval(() => fetchMetrics(true), 2 * 60 * 1000);
    
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex items-center space-x-2">
          <Loader2 className="h-5 w-5 animate-spin" />
          <span>Loading performance metrics...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header with refresh */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Performance Analytics</h2>
          <p className="text-muted-foreground">
            System performance metrics and processing efficiency analysis
          </p>
        </div>
        
        <div className="flex items-center space-x-4">
          {lastUpdated && (
            <span className="text-sm text-muted-foreground">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </span>
          )}
          
          <Button
            onClick={() => fetchMetrics()}
            disabled={refreshing}
            variant="outline"
            size="sm"
          >
            {refreshing ? (
              <Loader2 className="h-4 w-4 animate-spin mr-2" />
            ) : (
              <RefreshCw className="h-4 w-4 mr-2" />
            )}
            Refresh
          </Button>
        </div>
      </div>

      {/* Performance KPIs */}
      <PerformanceKPIs metrics={metrics} />

      {/* Performance Charts */}
      <PerformanceCharts metrics={metrics} />

      {/* Performance Details */}
      <PerformanceDetails metrics={metrics} />
    </div>
  );
}
