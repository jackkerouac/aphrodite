import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { TestTube, CheckCircle, XCircle, Clock, Image, Zap } from 'lucide-react';

interface DetectionTestData {
  test_passed: boolean;
  detected_resolution: string;
  used_image: string;
  detection_method: string;
  processing_time_ms: number;
}

interface DetectionTestCardProps {
  data: DetectionTestData;
}

export function DetectionTestCard({ data }: DetectionTestCardProps) {
  const getPerformanceBadge = (time: number) => {
    if (time < 30) return { variant: "default" as const, label: "Excellent" };
    if (time < 60) return { variant: "secondary" as const, label: "Good" };
    if (time < 100) return { variant: "outline" as const, label: "Fair" };
    return { variant: "destructive" as const, label: "Slow" };
  };

  const performance = getPerformanceBadge(data.processing_time_ms);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <TestTube className="h-4 w-4" />
          Enhanced Detection Test Results
          {data.test_passed ? (
            <Badge variant="default" className="flex items-center gap-1">
              <CheckCircle className="h-3 w-3" />
              Passed
            </Badge>
          ) : (
            <Badge variant="destructive" className="flex items-center gap-1">
              <XCircle className="h-3 w-3" />
              Failed
            </Badge>
          )}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Test Results Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="text-sm font-medium">Detected Resolution</span>
              <Badge variant="outline">{data.detected_resolution}</Badge>
            </div>
            
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="text-sm font-medium flex items-center gap-2">
                <Image className="h-3 w-3" />
                Used Image
              </span>
              <Badge variant="secondary">{data.used_image}</Badge>
            </div>
          </div>

          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="text-sm font-medium flex items-center gap-2">
                <Zap className="h-3 w-3" />
                Detection Method
              </span>
              <Badge variant={data.detection_method === 'Enhanced' ? 'default' : 'outline'}>
                {data.detection_method}
              </Badge>
            </div>
            
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="text-sm font-medium flex items-center gap-2">
                <Clock className="h-3 w-3" />
                Processing Time
              </span>
              <Badge variant={performance.variant}>
                {data.processing_time_ms}ms ({performance.label})
              </Badge>
            </div>
          </div>
        </div>

        {/* Test Status Alert */}
        {data.test_passed ? (
          <Alert>
            <CheckCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Test Successful!</strong> The resolution detection system is working correctly. 
              {data.detection_method === 'Enhanced' ? 
                ' Enhanced detection is active and properly identifying resolution variants.' :
                ' Legacy detection is active - consider enabling enhanced detection for better HDR/DV support.'
              }
            </AlertDescription>
          </Alert>
        ) : (
          <Alert variant="destructive">
            <XCircle className="h-4 w-4" />
            <AlertDescription>
              <strong>Test Failed!</strong> There may be an issue with the resolution detection system. 
              Check your image directory and mappings, or try clearing the cache.
            </AlertDescription>
          </Alert>
        )}

        {/* Performance Insights */}
        <div className="space-y-2">
          <h4 className="font-medium">Performance Analysis</h4>
          <div className="p-3 bg-muted rounded-lg space-y-2">
            {data.processing_time_ms < 60 && (
              <div className="text-sm text-green-700">
                ✓ Processing time is excellent ({data.processing_time_ms}ms)
              </div>
            )}
            
            {data.detection_method === 'Enhanced' && (
              <div className="text-sm text-blue-700">
                ✓ Enhanced detection active - HDR and Dolby Vision support enabled
              </div>
            )}
            
            {data.used_image.includes('hdr') && (
              <div className="text-sm text-purple-700">
                ✓ HDR variant image selected correctly
              </div>
            )}
            
            {data.used_image.includes('dv') && (
              <div className="text-sm text-purple-700">
                ✓ Dolby Vision variant image selected correctly
              </div>
            )}
            
            {data.processing_time_ms > 100 && (
              <div className="text-sm text-yellow-700">
                ⚠ Processing time is slower than expected - consider enabling caching
              </div>
            )}
          </div>
        </div>

        {/* Recommendations */}
        {data.detection_method === 'Legacy' && (
          <Alert>
            <AlertDescription>
              <strong>Recommendation:</strong> Enable Enhanced Detection in the Enhanced Detection tab 
              for better HDR, Dolby Vision, and 1440p resolution support.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
