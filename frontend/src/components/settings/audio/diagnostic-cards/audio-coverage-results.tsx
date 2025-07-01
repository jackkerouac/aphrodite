import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { AlertCircle, CheckCircle, XCircle, AudioWaveform, FileImage } from 'lucide-react';
import { AudioCoverageReport } from '../types';

interface AudioCoverageResultsProps {
  coverageData: AudioCoverageReport | null;
  onRunAnalysis: () => void;
  loading: boolean;
}

export function AudioCoverageResults({ coverageData, onRunAnalysis, loading }: AudioCoverageResultsProps) {
  if (!coverageData) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Audio Image Coverage Analysis
          </CardTitle>
          <CardDescription>
            Analyze your audio image collection for gaps and coverage
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button onClick={onRunAnalysis} disabled={loading}>
            {loading ? 'Analyzing...' : 'Run Coverage Analysis'}
          </Button>
        </CardContent>
      </Card>
    );
  }

  const totalFormats = Object.keys(coverageData.coverage_by_audio_format).length;
  const formatsWithBase = Object.values(coverageData.coverage_by_audio_format)
    .filter(format => format.has_base).length;
  const coveragePercentage = totalFormats > 0 ? Math.round((formatsWithBase / totalFormats) * 100) : 0;

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <FileImage className="h-5 w-5" />
            Audio Image Coverage Analysis
          </CardTitle>
          <CardDescription>
            Analysis of your audio image collection and coverage gaps
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Summary Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="bg-muted/50 p-3 rounded-md text-center">
              <div className="text-2xl font-bold">{coverageData.total_images}</div>
              <div className="text-sm text-muted-foreground">Total Images</div>
            </div>
            <div className="bg-muted/50 p-3 rounded-md text-center">
              <div className="text-2xl font-bold">{totalFormats}</div>
              <div className="text-sm text-muted-foreground">Audio Formats</div>
            </div>
            <div className="bg-muted/50 p-3 rounded-md text-center">
              <div className="text-2xl font-bold">{coverageData.atmos_images.length}</div>
              <div className="text-sm text-muted-foreground">Atmos Images</div>
            </div>
            <div className="bg-muted/50 p-3 rounded-md text-center">
              <div className="text-2xl font-bold">{coverageData.dts_x_images.length}</div>
              <div className="text-sm text-muted-foreground">DTS-X Images</div>
            </div>
          </div>

          {/* Coverage Progress */}
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm font-medium">Base Format Coverage</span>
              <span className="text-sm text-muted-foreground">{formatsWithBase}/{totalFormats}</span>
            </div>
            <Progress value={coveragePercentage} className="w-full" />
            <div className="text-xs text-muted-foreground">
              {coveragePercentage}% of audio formats have base images
            </div>
          </div>

          <Button 
            onClick={onRunAnalysis} 
            disabled={loading}
            variant="outline" 
            size="sm"
          >
            {loading ? 'Analyzing...' : 'Refresh Analysis'}
          </Button>
        </CardContent>
      </Card>

      {/* Format Coverage Details */}
      <Card>
        <CardHeader>
          <CardTitle>Format Coverage Details</CardTitle>
          <CardDescription>
            Detailed breakdown of audio format image availability
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3 max-h-60 overflow-y-auto">
            {Object.entries(coverageData.coverage_by_audio_format).map(([format, data]) => (
              <div key={format} className="border rounded-md p-3">
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <AudioWaveform className="h-4 w-4" />
                    <span className="font-medium">{format.toUpperCase()}</span>
                    {data.has_base ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                  </div>
                  <Badge variant={data.has_base ? "default" : "destructive"}>
                    {data.available_variants.length} available
                  </Badge>
                </div>
                
                {data.available_variants.length > 0 && (
                  <div className="mb-2">
                    <div className="text-sm text-muted-foreground mb-1">Available:</div>
                    <div className="flex flex-wrap gap-1">
                      {data.available_variants.map(variant => (
                        <Badge key={variant} variant="outline" className="text-xs">
                          {variant}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
                
                {data.missing_variants.length > 0 && (
                  <div>
                    <div className="text-sm text-muted-foreground mb-1">Missing:</div>
                    <div className="flex flex-wrap gap-1">
                      {data.missing_variants.map(variant => (
                        <Badge key={variant} variant="secondary" className="text-xs">
                          {variant}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Standalone Images */}
      {coverageData.standalone_images.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Standalone Images</CardTitle>
            <CardDescription>
              Images that don't belong to specific format categories
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex flex-wrap gap-2">
              {coverageData.standalone_images.map(image => (
                <Badge key={image} variant="outline">
                  {image}
                </Badge>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Fallback Coverage */}
      {Object.keys(coverageData.fallback_coverage).length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle>Fallback Coverage</CardTitle>
            <CardDescription>
              Automatic fallback rules for missing images
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {Object.entries(coverageData.fallback_coverage).map(([source, fallback]) => (
                <div key={source} className="flex items-center justify-between p-2 border rounded">
                  <span className="font-medium">{source}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-muted-foreground">→</span>
                    <span>{fallback.target}</span>
                    {fallback.target_available ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <AlertCircle className="h-4 w-4 text-yellow-500" />
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Premium Audio Features */}
      <Card>
        <CardHeader>
          <CardTitle>Premium Audio Features</CardTitle>
          <CardDescription>
            Dolby Atmos and DTS-X image availability
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <AudioWaveform className="h-4 w-4" />
                <span className="font-medium">Dolby Atmos Images</span>
                <Badge variant="outline">{coverageData.atmos_images.length}</Badge>
              </div>
              <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                {coverageData.atmos_images.map(image => (
                  <Badge key={image} variant="secondary" className="text-xs">
                    {image}
                  </Badge>
                ))}
                {coverageData.atmos_images.length === 0 && (
                  <span className="text-sm text-muted-foreground italic">No Atmos images found</span>
                )}
              </div>
            </div>
            
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <AudioWaveform className="h-4 w-4" />
                <span className="font-medium">DTS-X Images</span>
                <Badge variant="outline">{coverageData.dts_x_images.length}</Badge>
              </div>
              <div className="flex flex-wrap gap-1 max-h-20 overflow-y-auto">
                {coverageData.dts_x_images.map(image => (
                  <Badge key={image} variant="secondary" className="text-xs">
                    {image}
                  </Badge>
                ))}
                {coverageData.dts_x_images.length === 0 && (
                  <span className="text-sm text-muted-foreground italic">No DTS-X images found</span>
                )}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
