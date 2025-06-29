import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Slider } from '@/components/ui/slider';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Badge } from '@/components/ui/badge';
import { Gauge, Zap, Clock, Database } from 'lucide-react';
import { ResolutionSettings } from './types';

interface PerformanceTabProps {
  settings: ResolutionSettings;
  updateSetting: (section: keyof ResolutionSettings, key: string, value: any) => void;
}

export function PerformanceTab({ settings, updateSetting }: PerformanceTabProps) {
  const getCurrentEstimatedSpeed = () => {
    const baseSpeed = 255; // ms for series processing
    let estimatedSpeed = baseSpeed;
    
    if (settings.performance.enable_parallel_processing) {
      estimatedSpeed = estimatedSpeed * 0.3; // 70% improvement
    }
    
    if (settings.performance.enable_caching) {
      estimatedSpeed = estimatedSpeed * 0.02; // 98% improvement for cached
    }
    
    return Math.round(estimatedSpeed);
  };

  const getSpeedBadgeVariant = (speed: number) => {
    if (speed < 20) return "default"; // Very fast
    if (speed < 100) return "secondary"; // Fast  
    if (speed < 200) return "outline"; // Medium
    return "destructive"; // Slow
  };

  const currentSpeed = getCurrentEstimatedSpeed();

  return (
    <div className="space-y-6">
      {/* Performance Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Gauge className="h-5 w-5" />
            Performance Overview
          </CardTitle>
          <CardDescription>
            Optimize processing speed for large media libraries
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-2">
              <Clock className="h-4 w-4" />
              <span className="font-medium">Estimated TV Series Processing Time:</span>
            </div>
            <Badge variant={getSpeedBadgeVariant(currentSpeed)} className="text-lg px-3 py-1">
              {currentSpeed}ms
            </Badge>
          </div>
          
          <Alert className="mt-4">
            <Zap className="h-4 w-4" />
            <AlertDescription>
              <strong>Performance Impact:</strong> Movie processing time remains ~55ms. TV series processing varies based on your settings above.
            </AlertDescription>
          </Alert>
        </CardContent>
      </Card>

      {/* Parallel Processing */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="h-5 w-5" />
            Parallel Episode Processing
          </CardTitle>
          <CardDescription>
            Process TV series episodes concurrently for faster detection
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Switch
              id="enable-parallel-processing"
              checked={settings.performance.enable_parallel_processing}
              onCheckedChange={(checked) => updateSetting('performance', 'enable_parallel_processing', checked)}
            />
            <Label htmlFor="enable-parallel-processing" className="font-medium">
              Enable Parallel Processing
            </Label>
          </div>
          
          {settings.performance.enable_parallel_processing ? (
            <Alert>
              <Zap className="h-4 w-4" />
              <AlertDescription>
                <strong>Enabled:</strong> TV series episodes will be processed concurrently, reducing processing time by ~70%.
              </AlertDescription>
            </Alert>
          ) : (
            <Alert>
              <AlertDescription>
                <strong>Disabled:</strong> Episodes will be processed sequentially. This is more resource-friendly but slower.
              </AlertDescription>
            </Alert>
          )}

          {/* Episodes to Sample */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="episodes-sample">Episodes to Sample</Label>
              <Badge variant="outline">{settings.performance.max_episodes_to_sample} episodes</Badge>
            </div>
            <Slider
              id="episodes-sample"
              min={1}
              max={20}
              step={1}
              value={[settings.performance.max_episodes_to_sample]}
              onValueChange={(value) => updateSetting('performance', 'max_episodes_to_sample', value[0])}
              disabled={!settings.performance.enable_parallel_processing}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>1 episode (fastest)</span>
              <span>20 episodes (most accurate)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Caching */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Database className="h-5 w-5" />
            Resolution Caching
          </CardTitle>
          <CardDescription>
            Cache TV series resolution results to avoid re-processing
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center space-x-2">
            <Switch
              id="enable-caching"
              checked={settings.performance.enable_caching}
              onCheckedChange={(checked) => updateSetting('performance', 'enable_caching', checked)}
            />
            <Label htmlFor="enable-caching" className="font-medium">
              Enable Resolution Caching
            </Label>
          </div>
          
          {settings.performance.enable_caching ? (
            <Alert>
              <Database className="h-4 w-4" />
              <AlertDescription>
                <strong>Enabled:</strong> Series resolution results will be cached, reducing repeated processing to ~5ms.
              </AlertDescription>
            </Alert>
          ) : (
            <Alert>
              <AlertDescription>
                <strong>Disabled:</strong> Series will be re-processed every time. Use if you frequently change video files.
              </AlertDescription>
            </Alert>
          )}

          {/* Cache TTL */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <Label htmlFor="cache-ttl">Cache Duration</Label>
              <Badge variant="outline">{settings.performance.cache_ttl_hours} hours</Badge>
            </div>
            <Slider
              id="cache-ttl"
              min={1}
              max={168}
              step={1}
              value={[settings.performance.cache_ttl_hours]}
              onValueChange={(value) => updateSetting('performance', 'cache_ttl_hours', value[0])}
              disabled={!settings.performance.enable_caching}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-muted-foreground">
              <span>1 hour (frequent updates)</span>
              <span>1 week (stable library)</span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Performance Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Performance Tips</CardTitle>
          <CardDescription>
            Recommendations for optimizing resolution detection speed
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <Badge variant="outline" className="mt-0.5">Tip 1</Badge>
              <div>
                <p className="font-medium">Enable both parallel processing and caching</p>
                <p className="text-sm text-muted-foreground">
                  This combination provides the best performance improvement for large TV libraries.
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Badge variant="outline" className="mt-0.5">Tip 2</Badge>
              <div>
                <p className="font-medium">Sample 3-5 episodes for most series</p>
                <p className="text-sm text-muted-foreground">
                  This provides good accuracy while maintaining speed. Only increase for very inconsistent series.
                </p>
              </div>
            </div>
            
            <div className="flex items-start gap-3">
              <Badge variant="outline" className="mt-0.5">Tip 3</Badge>
              <div>
                <p className="font-medium">Use longer cache duration for stable libraries</p>
                <p className="text-sm text-muted-foreground">
                  If you rarely change video files, set cache duration to 24+ hours for maximum speed.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
