import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Calendar } from 'lucide-react';
import type { PerformanceMetrics } from '../types';

interface PerformanceChartsProps {
  metrics: PerformanceMetrics | null;
}

const formatDateOnly = (dateString: string) => {
  const date = new Date(dateString);
  return date.toLocaleDateString('en-US', { 
    month: 'short', 
    day: 'numeric'
  });
};

const getLoadScoreColor = (score: number) => {
  if (score >= 5) return 'text-red-600';
  if (score >= 2) return 'text-yellow-600';
  return 'text-green-600';
};

const getSuccessRateVariant = (rate: number) => {
  if (rate >= 95) return 'default';
  if (rate >= 80) return 'secondary';
  return 'destructive';
};

export function PerformanceCharts({ metrics }: PerformanceChartsProps) {
  if (!metrics || metrics.system_load_trends.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>System Load Trends</CardTitle>
          <CardDescription>Daily processing load over the last 7 days</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center text-muted-foreground py-8">
            <Calendar className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p className="text-sm">No trend data available</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  // Calculate trend direction
  const trends = metrics.system_load_trends;
  const recentTrend = trends.length >= 2 ? 
    trends[trends.length - 1].load_score - trends[trends.length - 2].load_score : 0;

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center space-x-2">
          <span>System Load Trends</span>
          {recentTrend > 0 ? (
            <TrendingUp className="h-4 w-4 text-red-500" />
          ) : recentTrend < 0 ? (
            <TrendingDown className="h-4 w-4 text-green-500" />
          ) : null}
        </CardTitle>
        <CardDescription>
          Daily processing load and success rates over the last 7 days
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {trends.map((trend, index) => (
            <div key={trend.date} className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex flex-col">
                <span className="font-medium">
                  {formatDateOnly(trend.date)}
                </span>
                <span className="text-xs text-muted-foreground">
                  {trend.total_jobs} jobs • {trend.total_posters} posters
                </span>
              </div>
              
              <div className="flex items-center space-x-3">
                <Badge variant={getSuccessRateVariant(trend.success_rate)}>
                  {trend.success_rate.toFixed(1)}%
                </Badge>
                
                <div className="text-right">
                  <div className={`text-sm font-medium ${getLoadScoreColor(trend.load_score)}`}>
                    Load: {trend.load_score.toFixed(1)}
                  </div>
                  <div className="text-xs text-muted-foreground">
                    {index === trends.length - 1 ? 'Latest' : 
                     index === trends.length - 2 ? 'Previous' : ''}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
        
        {trends.length > 0 && (
          <div className="mt-4 p-3 bg-muted rounded-lg">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted-foreground">7-day Summary:</span>
              <div className="flex space-x-4">
                <span>
                  Avg Load: {(trends.reduce((sum, t) => sum + t.load_score, 0) / trends.length).toFixed(1)}
                </span>
                <span>
                  Avg Success: {(trends.reduce((sum, t) => sum + t.success_rate, 0) / trends.length).toFixed(1)}%
                </span>
              </div>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
