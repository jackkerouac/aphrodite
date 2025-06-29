import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Database, TrendingUp, Clock } from 'lucide-react';
import { CacheStats } from '../types';

interface CacheStatsCardProps {
  data: CacheStats;
}

export function CacheStatsCard({ data }: CacheStatsCardProps) {
  const getHitRateVariant = (rate: number) => {
    if (rate >= 90) return "default";
    if (rate >= 70) return "secondary";
    if (rate >= 50) return "outline";
    return "destructive";
  };

  const formatDate = (isoString: string) => {
    return new Date(isoString).toLocaleString();
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Database className="h-4 w-4" />
          Cache Performance Statistics
          <Badge variant={getHitRateVariant(data.hit_rate_percent)}>
            {data.hit_rate_percent}% hit rate
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Hit Rate Progress */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm font-medium">Cache Hit Rate</span>
            <span className="text-sm text-muted-foreground">{data.hit_rate_percent}%</span>
          </div>
          <Progress value={data.hit_rate_percent} className="w-full" />
          <div className="text-xs text-muted-foreground">
            Higher hit rates indicate better performance
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center p-3 border rounded-lg">
            <div className="text-2xl font-bold text-green-600">{data.total_hits}</div>
            <div className="text-sm text-muted-foreground">Cache Hits</div>
          </div>
          <div className="text-center p-3 border rounded-lg">
            <div className="text-2xl font-bold text-red-600">{data.total_misses}</div>
            <div className="text-sm text-muted-foreground">Cache Misses</div>
          </div>
          <div className="text-center p-3 border rounded-lg">
            <div className="text-2xl font-bold">{data.cache_size}</div>
            <div className="text-sm text-muted-foreground">Cached Items</div>
          </div>
          <div className="text-center p-3 border rounded-lg">
            <div className="text-2xl font-bold">{data.ttl_hours}h</div>
            <div className="text-sm text-muted-foreground">TTL Duration</div>
          </div>
        </div>

        {/* Performance Metrics */}
        <div className="space-y-3">
          <h4 className="font-medium flex items-center gap-2">
            <TrendingUp className="h-4 w-4" />
            Performance Insights
          </h4>
          
          <div className="space-y-2">
            <div className="flex items-center justify-between p-2 border rounded">
              <span className="text-sm">Total Requests</span>
              <Badge variant="outline">{data.total_hits + data.total_misses}</Badge>
            </div>
            
            <div className="flex items-center justify-between p-2 border rounded">
              <span className="text-sm">Time Saved (estimated)</span>
              <Badge variant="secondary">
                {Math.round((data.total_hits * 250) / 1000)}s
              </Badge>
            </div>
            
            <div className="flex items-center justify-between p-2 border rounded">
              <span className="text-sm flex items-center gap-2">
                <Clock className="h-3 w-3" />
                Last Cleanup
              </span>
              <span className="text-xs text-muted-foreground">
                {formatDate(data.last_cleanup)}
              </span>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        {data.hit_rate_percent < 70 && (
          <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="font-medium text-yellow-800">Low Hit Rate Detected</div>
            <div className="text-sm text-yellow-700 mt-1">
              Consider increasing cache TTL or checking if your media library changes frequently.
            </div>
          </div>
        )}
        
        {data.hit_rate_percent >= 90 && (
          <div className="p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="font-medium text-green-800">Excellent Cache Performance</div>
            <div className="text-sm text-green-700 mt-1">
              Your cache is working optimally and saving significant processing time.
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
