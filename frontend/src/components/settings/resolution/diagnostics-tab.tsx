import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Search, Database, TestTube, BarChart3 } from 'lucide-react';
import { ResolutionSettings, DiagnosticResults } from './types';
import { ImageCoverageCard } from './diagnostic-cards/image-coverage-card';
import { CacheStatsCard } from './diagnostic-cards/cache-stats-card';
import { DetectionTestCard } from './diagnostic-cards/detection-test-card';

interface DiagnosticsTabProps {
  settings: ResolutionSettings;
  // Add diagnostic functions from hooks
  runImageCoverageAnalysis: () => Promise<any>;
  getCacheStats: () => Promise<any>;
  clearResolutionCache: () => Promise<any>;
  testEnhancedDetection: () => Promise<any>;
}

export function DiagnosticsTab({ 
  settings,
  runImageCoverageAnalysis,
  getCacheStats,
  clearResolutionCache,
  testEnhancedDetection
}: DiagnosticsTabProps) {
  const [diagnosticResults, setDiagnosticResults] = useState<DiagnosticResults>({});
  const [isRunningDiagnostic, setIsRunningDiagnostic] = useState<string | null>(null);

  // Main diagnostic functions
  const runCoverageAnalysis = async () => {
    setIsRunningDiagnostic('coverage');
    try {
      const results = await runImageCoverageAnalysis();
      setDiagnosticResults(prev => ({ ...prev, imageCoverage: results }));
    } catch (error) {
      console.error('Coverage analysis failed:', error);
    } finally {
      setIsRunningDiagnostic(null);
    }
  };

  const clearCache = async () => {
    setIsRunningDiagnostic('cache');
    try {
      await clearResolutionCache();
      setDiagnosticResults(prev => ({ ...prev, cacheStats: undefined }));
    } catch (error) {
      console.error('Cache clear failed:', error);
    } finally {
      setIsRunningDiagnostic(null);
    }
  };

  const getStats = async () => {
    setIsRunningDiagnostic('cacheStats');
    try {
      const stats = await getCacheStats();
      setDiagnosticResults(prev => ({ ...prev, cacheStats: stats }));
    } catch (error) {
      console.error('Cache stats failed:', error);
    } finally {
      setIsRunningDiagnostic(null);
    }
  };

  const testDetection = async () => {
    setIsRunningDiagnostic('test');
    try {
      const testResults = await testEnhancedDetection();
      setDiagnosticResults(prev => ({ ...prev, testResults }));
    } catch (error) {
      console.error('Detection test failed:', error);
    } finally {
      setIsRunningDiagnostic(null);
    }
  };

  return (
    <div className="space-y-6">
      {/* Diagnostic Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="h-5 w-5" />
            Diagnostic Tools
          </CardTitle>
          <CardDescription>
            Analyze and troubleshoot resolution detection performance
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Button
              onClick={runCoverageAnalysis}
              disabled={isRunningDiagnostic === 'coverage'}
              className="flex items-center gap-2"
            >
              <Search className="h-4 w-4" />
              {isRunningDiagnostic === 'coverage' ? 'Analyzing...' : 'Analyze Image Coverage'}
            </Button>
            
            <Button
              onClick={getStats}
              disabled={isRunningDiagnostic === 'cacheStats' || !settings.performance.enable_caching}
              className="flex items-center gap-2"
              variant="outline"
            >
              <Database className="h-4 w-4" />
              {isRunningDiagnostic === 'cacheStats' ? 'Loading...' : 'Get Cache Stats'}
            </Button>
            
            <Button
              onClick={clearCache}
              disabled={isRunningDiagnostic === 'cache' || !settings.performance.enable_caching}
              className="flex items-center gap-2"
              variant="outline"
            >
              <Database className="h-4 w-4" />
              {isRunningDiagnostic === 'cache' ? 'Clearing...' : 'Clear Resolution Cache'}
            </Button>
            
            <Button
              onClick={testDetection}
              disabled={isRunningDiagnostic === 'test'}
              className="flex items-center gap-2"
              variant="outline"
            >
              <TestTube className="h-4 w-4" />
              {isRunningDiagnostic === 'test' ? 'Testing...' : 'Test Enhanced Detection'}
            </Button>
          </div>
          
          {!settings.performance.enable_caching && (
            <Alert className="mt-4">
              <AlertDescription>
                Cache-related diagnostics are disabled because caching is turned off in Performance settings.
              </AlertDescription>
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Results Cards */}
      {diagnosticResults.imageCoverage && (
        <ImageCoverageCard data={diagnosticResults.imageCoverage} />
      )}
      
      {diagnosticResults.cacheStats && (
        <CacheStatsCard data={diagnosticResults.cacheStats} />
      )}
      
      {diagnosticResults.testResults && (
        <DetectionTestCard data={diagnosticResults.testResults} />
      )}
    </div>
  );
}
