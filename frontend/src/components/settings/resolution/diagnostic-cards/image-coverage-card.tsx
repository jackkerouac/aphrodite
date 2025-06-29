import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Image, CheckCircle, XCircle, AlertTriangle } from 'lucide-react';
import { ImageCoverageReport } from '../types';

interface ImageCoverageCardProps {
  data: ImageCoverageReport;
}

export function ImageCoverageCard({ data }: ImageCoverageCardProps) {
  const totalMissing = data.missing_combinations.length;
  const totalResolutions = Object.keys(data.coverage_by_resolution).length;
  const coveragePercentage = Math.round(((data.total_images - totalMissing) / data.total_images) * 100);

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Image className="h-4 w-4" />
          Image Coverage Analysis
          <Badge variant={coveragePercentage > 80 ? "default" : "destructive"}>
            {coveragePercentage}% coverage
          </Badge>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Summary Stats */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold">{data.total_images}</div>
            <div className="text-sm text-muted-foreground">Total Images</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold">{totalResolutions}</div>
            <div className="text-sm text-muted-foreground">Resolutions</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{data.total_images - totalMissing}</div>
            <div className="text-sm text-muted-foreground">Available</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{totalMissing}</div>
            <div className="text-sm text-muted-foreground">Missing</div>
          </div>
        </div>

        {/* Resolution Coverage */}
        <div className="space-y-3">
          <h4 className="font-medium">Coverage by Resolution</h4>
          {Object.entries(data.coverage_by_resolution).map(([resolution, info]) => (
            <div key={resolution} className="border rounded-lg p-3">
              <div className="flex items-center justify-between mb-2">
                <span className="font-medium">{resolution}</span>
                <div className="flex items-center gap-2">
                  {info.has_base ? (
                    <CheckCircle className="h-4 w-4 text-green-600" />
                  ) : (
                    <XCircle className="h-4 w-4 text-red-600" />
                  )}
                  <Badge variant="outline">
                    {info.available_variants.length} variants
                  </Badge>
                </div>
              </div>
              
              <div className="space-y-2">
                <div>
                  <span className="text-sm font-medium text-green-700">Available:</span>
                  <div className="flex flex-wrap gap-1 mt-1">
                    {info.available_variants.map(variant => (
                      <Badge key={variant} variant="secondary" className="text-xs">
                        {variant}
                      </Badge>
                    ))}
                  </div>
                </div>
                
                {info.missing_variants.length > 0 && (
                  <div>
                    <span className="text-sm font-medium text-red-700">Missing:</span>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {info.missing_variants.map(variant => (
                        <Badge key={variant} variant="destructive" className="text-xs">
                          {variant}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Fallback Coverage */}
        <div className="space-y-2">
          <h4 className="font-medium">Fallback Rules Status</h4>
          {Object.entries(data.fallback_coverage).map(([source, fallback]) => (
            <div key={source} className="flex items-center justify-between p-2 border rounded">
              <span className="text-sm">{source} → {fallback.target}</span>
              {fallback.target_available ? (
                <Badge variant="default" className="text-xs">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Available
                </Badge>
              ) : (
                <Badge variant="destructive" className="text-xs">
                  <XCircle className="h-3 w-3 mr-1" />
                  Missing
                </Badge>
              )}
            </div>
          ))}
        </div>

        {/* Standalone Images */}
        {data.standalone_images.length > 0 && (
          <div className="space-y-2">
            <h4 className="font-medium">Standalone Images</h4>
            <div className="flex flex-wrap gap-1">
              {data.standalone_images.map(image => (
                <Badge key={image} variant="outline" className="text-xs">
                  {image}
                </Badge>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        {totalMissing > 0 && (
          <Alert>
            <AlertTriangle className="h-4 w-4" />
            <AlertDescription>
              <strong>Missing {totalMissing} images.</strong> Consider adding these images to improve coverage, 
              or adjust your fallback rules to handle missing variants.
            </AlertDescription>
          </Alert>
        )}
      </CardContent>
    </Card>
  );
}
