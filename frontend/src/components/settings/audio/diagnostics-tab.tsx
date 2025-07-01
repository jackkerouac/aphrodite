import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Play, Trash2, Activity, Database, TestTube, AudioWaveform } from 'lucide-react';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';
import { AudioSettings, AudioCacheStats, AudioDetectionTestResult, AudioCoverageReport } from './types';
import { AudioCoverageResults } from './diagnostic-cards/audio-coverage-results';

interface DiagnosticsTabProps {
  settings: AudioSettings;
  runAudioCoverageAnalysis: () => Promise<AudioCoverageReport | null>;
  getCacheStats: () => Promise<AudioCacheStats | null>;
  clearAudioCache: () => Promise<boolean>;
  testEnhancedDetection: (testData?: any) => Promise<AudioDetectionTestResult | null>;
}

export function DiagnosticsTab({
  settings,
  runAudioCoverageAnalysis,
  getCacheStats,
  clearAudioCache,
  testEnhancedDetection
}: DiagnosticsTabProps) {
  const [coverageLoading, setCoverageLoading] = useState(false);
  const [cacheLoading, setCacheLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [clearingCache, setClearingCache] = useState(false);
  
  const [coverageData, setCoverageData] = useState<AudioCoverageReport | null>(null);
  const [cacheStats, setCacheStats] = useState<AudioCacheStats | null>(null);
  const [testResult, setTestResult] = useState<AudioDetectionTestResult | null>(null);

  // Auto-load cache stats on mount
  useEffect(() => {
    handleGetCacheStats();
  }, []);

  const handleCoverageAnalysis = async () => {
    setCoverageLoading(true);
    try {
      const result = await runAudioCoverageAnalysis();
      setCoverageData(result);
      if (result) {
        toast.success('Audio coverage analysis completed');
      }
    } finally {
      setCoverageLoading(false);
    }
  };

  const handleGetCacheStats = async () => {
    setCacheLoading(true);
    try {
      const result = await getCacheStats();
      setCacheStats(result);
    } finally {
      setCacheLoading(false);
    }
  };

  const handleClearCache = async () => {
    setClearingCache(true);
    try {
      const success = await clearAudioCache();
      if (success) {
        // Refresh cache stats after clearing
        await handleGetCacheStats();
      }
    } finally {
      setClearingCache(false);
    }
  };

  const handleTestDetection = async () => {
    setTestLoading(true);
    try {
      const result = await testEnhancedDetection();
      setTestResult(result);
      if (result) {
        toast.success(`Detection test ${result.test_passed ? 'passed' : 'failed'}`);
      }
    } finally {
      setTestLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Audio Detection Diagnostics
          </CardTitle>
          <CardDescription>
            Monitor and test your audio detection system performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button
              onClick={handleCoverageAnalysis}
              disabled={coverageLoading}
              variant="outline"
              className="h-20 flex-col"
            >
              {coverageLoading ? (
                <Loader2 className="h-5 w-5 animate-spin mb-2" />
              ) : (
                <AudioWaveform className="h-5 w-5 mb-2" />
              )}
              {coverageLoading ? 'Analyzing...' : 'Audio Coverage'}
            </Button>

            <Button
              onClick={handleGetCacheStats}
              disabled={cacheLoading}
              variant="outline"
              className="h-20 flex-col"
            >
              {cacheLoading ? (
                <Loader2 className="h-5 w-5 animate-spin mb-2" />
              ) : (
                <Database className="h-5 w-5 mb-2" />
              )}
              {cacheLoading ? 'Loading...' : 'Cache Stats'}
            </Button>

            <Button
              onClick={handleTestDetection}
              disabled={testLoading}
              variant="outline"
              className="h-20 flex-col"
            >
              {testLoading ? (
                <Loader2 className="h-5 w-5 animate-spin mb-2" />
              ) : (
                <TestTube className="h-5 w-5 mb-2" />
              )}
              {testLoading ? 'Testing...' : 'Test Detection'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Cache Statistics */}
      {cacheStats && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Cache Performance
            </CardTitle>
            <CardDescription>
              Audio detection cache statistics and performance metrics
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-muted/50 p-3 rounded-md text-center">
                <div className="text-2xl font-bold text-green-600">
                  {cacheStats.hit_rate_percent.toFixed(1)}%
                </div>
                <div className="text-sm text-muted-foreground">Hit Rate</div>
              </div>
              <div className="bg-muted/50 p-3 rounded-md text-center">
                <div className="text-2xl font-bold">{cacheStats.cache_size}</div>
                <div className="text-sm text-muted-foreground">Cached Items</div>
              </div>
              <div className="bg-muted/50 p-3 rounded-md text-center">
                <div className="text-2xl font-bold">{cacheStats.episode_samples_cached}</div>
                <div className="text-sm text-muted-foreground">Episode Samples</div>
              </div>
              <div className="bg-muted/50 p-3 rounded-md text-center">
                <div className="text-2xl font-bold">{cacheStats.ttl_hours}h</div>
                <div className="text-sm text-muted-foreground">TTL</div>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Total Hits:</span>
                  <Badge variant="outline">{cacheStats.total_hits}</Badge>
                </div>
                <div className="flex justify-between">
                  <span>Total Misses:</span>
                  <Badge variant="outline">{cacheStats.total_misses}</Badge>
                </div>
              </div>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span>Last Cleanup:</span>
                  <span className="font-mono text-xs">
                    {new Date(cacheStats.last_cleanup).toLocaleString()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Cache Status:</span>
                  <Badge variant={settings.Performance.enable_caching ? "default" : "secondary"}>
                    {settings.Performance.enable_caching ? "Enabled" : "Disabled"}
                  </Badge>
                </div>
              </div>
            </div>

            <div className="flex gap-2">
              <Button
                onClick={handleGetCacheStats}
                disabled={cacheLoading}
                variant="outline"
                size="sm"
              >
                {cacheLoading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
                Refresh Stats
              </Button>
              <Button
                onClick={handleClearCache}
                disabled={clearingCache || !settings.Performance.enable_caching}
                variant="destructive"
                size="sm"
              >
                {clearingCache ? (
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                ) : (
                  <Trash2 className="h-4 w-4 mr-2" />
                )}
                Clear Cache
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detection Test Results */}
      {testResult && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TestTube className="h-5 w-5" />
              Enhanced Detection Test Results
            </CardTitle>
            <CardDescription>
              Results from the latest audio detection test
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Test Status:</span>
                  <Badge variant={testResult.test_passed ? "default" : "destructive"}>
                    {testResult.test_passed ? "PASSED" : "FAILED"}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Detection Method:</span>
                  <Badge variant="outline">{testResult.detection_method}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Processing Time:</span>
                  <span className="font-mono">{testResult.processing_time_ms}ms</span>
                </div>
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between">
                  <span className="font-medium">Detected Audio:</span>
                  <Badge variant="secondary">{testResult.detected_audio}</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="font-medium">Used Image:</span>
                  <span className="font-mono text-sm">{testResult.used_image}</span>
                </div>
                <div className="grid grid-cols-2 gap-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Atmos:</span>
                    <Badge variant={testResult.atmos_detected ? "default" : "outline"} className="text-xs">
                      {testResult.atmos_detected ? "YES" : "NO"}
                    </Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">DTS-X:</span>
                    <Badge variant={testResult.dts_x_detected ? "default" : "outline"} className="text-xs">
                      {testResult.dts_x_detected ? "YES" : "NO"}
                    </Badge>
                  </div>
                </div>
              </div>
            </div>

            <Button
              onClick={handleTestDetection}
              disabled={testLoading}
              variant="outline"
              size="sm"
            >
              {testLoading ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <Play className="h-4 w-4 mr-2" />
              )}
              Run Test Again
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Audio Coverage Analysis */}
      <AudioCoverageResults
        coverageData={coverageData}
        onRunAnalysis={handleCoverageAnalysis}
        loading={coverageLoading}
      />

      {/* System Information */}
      <Card>
        <CardHeader>
          <CardTitle>Audio Detection System Status</CardTitle>
          <CardDescription>
            Current configuration and feature availability
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <h5 className="font-semibold">Enhanced Features</h5>
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Enhanced Detection:</span>
                  <Badge variant={settings.EnhancedDetection.enabled ? "default" : "secondary"}>
                    {settings.EnhancedDetection.enabled ? "ON" : "OFF"}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Parallel Processing:</span>
                  <Badge variant={settings.Performance.enable_parallel_processing ? "default" : "secondary"}>
                    {settings.Performance.enable_parallel_processing ? "ON" : "OFF"}
                  </Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Caching:</span>
                  <Badge variant={settings.Performance.enable_caching ? "default" : "secondary"}>
                    {settings.Performance.enable_caching ? "ON" : "OFF"}
                  </Badge>
                </div>
              </div>
            </div>
            
            <div className="space-y-2">
              <h5 className="font-semibold">Detection Patterns</h5>
              <div className="space-y-1">
                <div className="flex justify-between items-center">
                  <span className="text-sm">Atmos Patterns:</span>
                  <Badge variant="outline">{settings.EnhancedDetection.atmos_detection_patterns.length}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">DTS-X Patterns:</span>
                  <Badge variant="outline">{settings.EnhancedDetection.dts_x_detection_patterns.length}</Badge>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-sm">Priority Items:</span>
                  <Badge variant="outline">{settings.EnhancedDetection.priority_order.length}</Badge>
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
