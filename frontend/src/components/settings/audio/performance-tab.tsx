import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { Gauge, Zap, Clock, Database } from 'lucide-react';
import { AudioSettings } from './types';

interface PerformanceTabProps {
  settings: AudioSettings;
  updateSetting: (path: string, value: any) => void;
}

export function PerformanceTab({ settings, updateSetting }: PerformanceTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Gauge className="h-5 w-5" />
          Performance Settings
        </CardTitle>
        <CardDescription>
          Configure audio detection performance optimizations
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Parallel Processing */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Zap className="h-4 w-4" />
            <h4 className="text-lg font-semibold">Parallel Processing</h4>
            <Badge variant={settings.Performance.enable_parallel_processing ? "default" : "secondary"}>
              {settings.Performance.enable_parallel_processing ? "Enabled" : "Disabled"}
            </Badge>
          </div>
          
          <div className="space-y-4 pl-6 border-l-2 border-muted">
            <div className="flex items-center space-x-2">
              <Switch
                id="parallel-processing"
                checked={settings.Performance.enable_parallel_processing}
                onCheckedChange={(checked) => updateSetting('Performance.enable_parallel_processing', checked)}
              />
              <Label htmlFor="parallel-processing">Enable Parallel Processing for TV Series</Label>
            </div>
            
            <div className="text-sm text-muted-foreground">
              Processes multiple episodes simultaneously for improved performance. 
              Recommended for systems with multiple CPU cores.
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="max-episodes">Max Episodes to Sample (TV Series)</Label>
              <Input
                id="max-episodes"
                type="number"
                min="1"
                max="20"
                value={settings.Performance.max_episodes_to_sample}
                onChange={(e) => updateSetting('Performance.max_episodes_to_sample', parseInt(e.target.value) || 5)}
                disabled={!settings.Performance.enable_parallel_processing}
              />
              <div className="text-sm text-muted-foreground">
                Number of episodes to sample for audio detection in TV series. 
                Higher values provide more accuracy but use more resources.
              </div>
            </div>
          </div>
        </div>

        {/* Caching */}
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Database className="h-4 w-4" />
            <h4 className="text-lg font-semibold">Audio Detection Caching</h4>
            <Badge variant={settings.Performance.enable_caching ? "default" : "secondary"}>
              {settings.Performance.enable_caching ? "Enabled" : "Disabled"}
            </Badge>
          </div>
          
          <div className="space-y-4 pl-6 border-l-2 border-muted">
            <div className="flex items-center space-x-2">
              <Switch
                id="caching"
                checked={settings.Performance.enable_caching}
                onCheckedChange={(checked) => updateSetting('Performance.enable_caching', checked)}
              />
              <Label htmlFor="caching">Enable Audio Detection Caching</Label>
            </div>
            
            <div className="text-sm text-muted-foreground">
              Caches audio detection results to avoid re-processing the same media files. 
              Significantly improves performance for repeated operations.
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="cache-ttl">Cache TTL (Hours)</Label>
              <div className="flex items-center gap-2">
                <Clock className="h-4 w-4 text-muted-foreground" />
                <Input
                  id="cache-ttl"
                  type="number"
                  min="1"
                  max="168"
                  value={settings.Performance.cache_ttl_hours}
                  onChange={(e) => updateSetting('Performance.cache_ttl_hours', parseInt(e.target.value) || 24)}
                  disabled={!settings.Performance.enable_caching}
                />
              </div>
              <div className="text-sm text-muted-foreground">
                How long to keep cached audio detection results. 
                Default: 24 hours. Max: 168 hours (7 days).
              </div>
            </div>
          </div>
        </div>

        {/* Performance Summary */}
        <div className="bg-muted/50 p-4 rounded-md space-y-2">
          <h5 className="font-semibold">Performance Configuration Summary</h5>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>Parallel Processing:</span>
                <Badge variant={settings.Performance.enable_parallel_processing ? "default" : "outline"} className="text-xs">
                  {settings.Performance.enable_parallel_processing ? "ON" : "OFF"}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span>Episode Sampling:</span>
                <span className="font-mono">{settings.Performance.max_episodes_to_sample} episodes</span>
              </div>
            </div>
            <div className="space-y-1">
              <div className="flex justify-between">
                <span>Caching:</span>
                <Badge variant={settings.Performance.enable_caching ? "default" : "outline"} className="text-xs">
                  {settings.Performance.enable_caching ? "ON" : "OFF"}
                </Badge>
              </div>
              <div className="flex justify-between">
                <span>Cache Duration:</span>
                <span className="font-mono">{settings.Performance.cache_ttl_hours}h</span>
              </div>
            </div>
          </div>
          
          <div className="text-xs text-muted-foreground mt-2">
            💡 For best performance: Enable both parallel processing and caching
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
