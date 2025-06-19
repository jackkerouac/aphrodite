'use client';

import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { AlertCircle, Image as ImageIcon, Maximize2, Download, ExternalLink } from 'lucide-react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';

interface PosterPreviewProps {
  isGenerating: boolean;
  previewUrl?: string;
  sourcePoster?: string;
  selectedBadgeTypes: string[];
  error?: string;
  className?: string;
}

export function PosterPreview({
  isGenerating,
  previewUrl,
  sourcePoster,
  selectedBadgeTypes,
  error,
  className = ''
}: PosterPreviewProps) {
  const [imageError, setImageError] = useState(false);
  const [isFullscreenOpen, setIsFullscreenOpen] = useState(false);

  const handleImageError = () => {
    setImageError(true);
  };

  const handleImageLoad = () => {
    setImageError(false);
  };

  const handleDownload = async () => {
    if (!previewUrl) return;

    try {
      const response = await fetch(previewUrl);
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `aphrodite-preview-${Date.now()}.png`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      console.error('Error downloading preview:', error);
    }
  };

  const renderContent = () => {
    // Error state
    if (error) {
      return (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>
            {error}
          </AlertDescription>
        </Alert>
      );
    }

    // Loading state
    if (isGenerating) {
      return (
        <div className="flex flex-col items-center justify-center py-16 space-y-4">
          <div className="relative">
            <div className="h-16 w-16 animate-spin rounded-full border-4 border-muted border-t-primary" />
            <ImageIcon className="absolute top-1/2 left-1/2 h-6 w-6 -translate-x-1/2 -translate-y-1/2 text-muted-foreground" />
          </div>
          <div className="text-center space-y-2">
            <p className="text-sm font-medium">Generating preview...</p>
            <p className="text-xs text-muted-foreground">
              Applying {selectedBadgeTypes.length} badge type{selectedBadgeTypes.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>
      );
    }

    // Preview image state
    if (previewUrl && !imageError) {
      return (
        <div className="space-y-4">
          <div className="relative group">
            <img 
              src={previewUrl}
              alt="Preview Poster"
              className="w-full h-auto rounded-lg shadow-md transition-transform group-hover:scale-[1.02]"
              style={{ maxHeight: '500px', objectFit: 'contain' }}
              onError={handleImageError}
              onLoad={handleImageLoad}
            />
            
            {/* Overlay controls */}
            <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity space-x-2">
              <Dialog open={isFullscreenOpen} onOpenChange={setIsFullscreenOpen}>
                <DialogTrigger asChild>
                  <Button size="sm" variant="secondary" className="backdrop-blur-sm">
                    <Maximize2 className="h-4 w-4" />
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-4xl w-full h-[90vh]">
                  <DialogHeader>
                    <DialogTitle>Preview Poster - Full Size</DialogTitle>
                    <DialogDescription>
                      Enhanced with {selectedBadgeTypes.join(', ')} badges
                      {sourcePoster && ` using "${sourcePoster}"`}
                    </DialogDescription>
                  </DialogHeader>
                  <div className="flex-1 flex items-center justify-center overflow-auto">
                    <img 
                      src={previewUrl}
                      alt="Preview Poster - Full Size"
                      className="max-w-full max-h-full object-contain"
                    />
                  </div>
                </DialogContent>
              </Dialog>

              <Button size="sm" variant="secondary" onClick={handleDownload} className="backdrop-blur-sm">
                <Download className="h-4 w-4" />
              </Button>
            </div>
          </div>

          {/* Preview info */}
          <div className="text-center space-y-2">
            <div className="flex flex-wrap gap-1 justify-center">
              {selectedBadgeTypes.map((badgeType) => (
                <Badge key={badgeType} variant="secondary" className="text-xs">
                  {badgeType}
                </Badge>
              ))}
            </div>
            <p className="text-sm text-muted-foreground">
              Preview generated with {selectedBadgeTypes.length} badge type{selectedBadgeTypes.length !== 1 ? 's' : ''}
              {sourcePoster && (
                <span className="block text-xs mt-1">
                  Using "{sourcePoster}"
                </span>
              )}
            </p>
          </div>

          {/* Action buttons */}
          <div className="flex gap-2 justify-center">
            <Button variant="outline" size="sm" onClick={handleDownload}>
              <Download className="mr-2 h-4 w-4" />
              Download Preview
            </Button>
            <Button variant="outline" size="sm" onClick={() => setIsFullscreenOpen(true)}>
              <ExternalLink className="mr-2 h-4 w-4" />
              View Full Size
            </Button>
          </div>
        </div>
      );
    }

    // Placeholder state
    return (
      <div className="flex flex-col items-center justify-center py-16 space-y-4">
        <div className="relative">
          <ImageIcon className="h-16 w-16 text-muted-foreground/30" />
        </div>
        <div className="text-center space-y-2">
          <p className="text-sm text-muted-foreground">
            Your poster preview will appear here
          </p>
          <p className="text-xs text-muted-foreground">
            Select badge types and click "Generate Preview"
          </p>
        </div>
      </div>
    );
  };

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <ImageIcon className="h-5 w-5" />
          Preview Poster
        </CardTitle>
        <CardDescription>
          See how your selected badges will look on a poster
        </CardDescription>
      </CardHeader>
      
      <CardContent>
        {renderContent()}
      </CardContent>
    </Card>
  );
}
