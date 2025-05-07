import React, { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { AudioBadgeSettings } from '../hooks/useAudioBadgeSettings';

interface PreviewPanelProps {
  previewImage: string;
  togglePreviewImage: () => void;
  selectedAudioCodec: string;
  settings: AudioBadgeSettings;
  audioCodecImages: Record<string, string>;
}

const PreviewPanel: React.FC<PreviewPanelProps> = ({
  previewImage,
  togglePreviewImage,
  selectedAudioCodec,
  settings,
  audioCodecImages
}) => {
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });

  // Load image dimensions
  useEffect(() => {
    const imagePath = audioCodecImages[selectedAudioCodec] || audioCodecImages['dolby_atmos'];
    const img = new Image();
    img.src = imagePath;
    img.crossOrigin = 'anonymous';
    
    const handleLoad = () => {
      // Store the natural dimensions of the image
      const width = img.naturalWidth;
      const height = img.naturalHeight;
      setImageDimensions({ width, height });
      console.log(`Image loaded: ${selectedAudioCodec}, Size: ${width}x${height}`);
    };

    const handleError = (e: any) => {
      console.error(`Error loading image ${imagePath}:`, e);
      setImageDimensions({ width: 0, height: 0 });
    };

    img.onload = handleLoad;
    img.onerror = handleError;

    // Cleanup function
    return () => {
      img.onload = null;
      img.onerror = null;
    };
  }, [selectedAudioCodec, audioCodecImages]);

  // Calculate badge position based on settings
  const getBadgePosition = () => {
    const position = settings.position || 'top-right';
    
    // Position mapping - this controls the badge position on the poster
    switch (position) {
      case 'top-left':
        return { top: `${settings.margin}px`, left: `${settings.margin}px` };
      case 'top-center':
        return { top: `${settings.margin}px`, left: '50%', transform: 'translateX(-50%)' };
      case 'top-right':
        return { top: `${settings.margin}px`, right: `${settings.margin}px` };
      case 'bottom-left':
        return { bottom: `${settings.margin}px`, left: `${settings.margin}px` };
      case 'bottom-center':
        return { bottom: `${settings.margin}px`, left: '50%', transform: 'translateX(-50%)' };
      case 'bottom-right':
        return { bottom: `${settings.margin}px`, right: `${settings.margin}px` };
      default:
        return { top: `${settings.margin}px`, right: `${settings.margin}px` };
    }
  };

  // Get badge container style (the box around the badge)
  const getBadgeContainerStyle = () => {
    // Apply shadow if enabled
    let shadow = '';
    if (settings.shadow_toggle) {
      const shadowColor = settings.shadow_color || '#000000';
      // Convert hex to rgba to include transparency
      const r = parseInt(shadowColor.slice(1, 3), 16);
      const g = parseInt(shadowColor.slice(3, 5), 16);
      const b = parseInt(shadowColor.slice(5, 7), 16);
      shadow = `${settings.shadow_offset_x}px ${settings.shadow_offset_y}px ${settings.shadow_blur_radius}px rgba(${r}, ${g}, ${b}, 1)`;
    }

    // Convert hex to rgba for background and border
    const bgR = parseInt(settings.background_color.slice(1, 3), 16);
    const bgG = parseInt(settings.background_color.slice(3, 5), 16);
    const bgB = parseInt(settings.background_color.slice(5, 7), 16);
    
    const borderR = parseInt(settings.border_color.slice(1, 3), 16);
    const borderG = parseInt(settings.border_color.slice(3, 5), 16);
    const borderB = parseInt(settings.border_color.slice(5, 7), 16);

    return {
      position: 'absolute',
      zIndex: settings.z_index,
      boxShadow: shadow || 'none',
      backgroundColor: `rgba(${bgR}, ${bgG}, ${bgB}, ${settings.background_transparency})`,
      borderRadius: `${settings.border_radius}px`,
      border: `${settings.border_width}px solid rgba(${borderR}, ${borderG}, ${borderB}, ${settings.border_transparency})`,
      padding: '8px', // Add padding around the image
      ...getBadgePosition()
    };
  };

  // Get badge image style
  const getBadgeImageStyle = () => {
    return {
      width: 'auto',
      height: 'auto',
      maxWidth: '100%',
      transform: `scale(${settings.size / 100})`,
      transformOrigin: 'center',
      display: 'block',
    };
  };

  return (
    <Card className="h-full">
      <CardHeader className="pb-4">
        <CardTitle className="text-lg">Preview</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-col gap-4">
          <div className="relative bg-muted rounded-md overflow-hidden" style={{ minHeight: '400px' }}>
            {/* Background Image */}
            <img
              src={previewImage}
              alt="Poster Preview"
              className="w-full h-auto object-contain"
            />
            
            {/* Audio Badge */}
            <div style={getBadgeContainerStyle()}>
              <img
                src={audioCodecImages[selectedAudioCodec] || audioCodecImages['dolby_atmos']}
                alt={`${selectedAudioCodec} badge`}
                style={getBadgeImageStyle()}
              />
            </div>
          </div>
          
          {/* Toggle Preview Button */}
          <Button onClick={togglePreviewImage} variant="outline" className="w-full">
            Toggle Dark/Light Preview
          </Button>

          {/* Badge Information */}
          <div className="text-sm text-muted-foreground">
            <p>Selected Badge: <span className="font-medium">{selectedAudioCodec}</span></p>
            <p>Badge Size: {imageDimensions.width} x {imageDimensions.height}px</p>
            <p>Display Size: {Math.round(imageDimensions.width * (settings.size / 100))} x {Math.round(imageDimensions.height * (settings.size / 100))}px</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PreviewPanel;