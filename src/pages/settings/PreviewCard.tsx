// PreviewCard.tsx
import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';

interface PreviewCardProps {
    previewImage: string;
    togglePreviewImage: () => void;
    selectedResolution: string;
    settings: any;
    resolutionImages: Record<string, string>;
    imageDimensions: { width: number, height: number };
}

const PreviewCard: React.FC<PreviewCardProps> = ({
    previewImage,
    togglePreviewImage,
    selectedResolution,
    settings,
    resolutionImages,
}) => {
    // Get the image path for the selected resolution
    const imagePath = resolutionImages[selectedResolution] || resolutionImages['1080'];
    
    // Calculate position based on settings
    const getBadgePosition = () => {
        const position = settings.position || 'top-left';
        const margin = Number(settings.margin) || 10;
        const size = settings.size || 100; // Size as percentage
        
        // Calculate the necessary adjustment for position to maintain margin after scaling
        const getScaledPosition = () => {
            // If size is 100%, no adjustment needed
            if (size === 100) return margin;
            
            // For sizes less than 100%, need to reduce margin to keep correct positioning
            // For sizes greater than 100%, need to increase margin to keep correct positioning
            // This is necessary because the transform scale happens from the center of the element
            const scaleFactor = size / 100;
            return margin / scaleFactor;
        };
        
        let style = {
            position: 'absolute' as const,
            maxWidth: '150px',
            height: 'auto',
            transformOrigin: position.replace('-', ' '), // Transform from the corner point
        };
        
        // Position based on the selected option
        switch (position) {
            case 'top-left':
                return {
                    ...style,
                    top: getScaledPosition(),
                    left: getScaledPosition(),
                    transformOrigin: 'top left',
                };
            case 'top-right':
                return {
                    ...style,
                    top: getScaledPosition(),
                    right: getScaledPosition(),
                    transformOrigin: 'top right',
                };
            case 'bottom-left':
                return {
                    ...style,
                    bottom: getScaledPosition(),
                    left: getScaledPosition(),
                    transformOrigin: 'bottom left',
                };
            case 'bottom-right':
                return {
                    ...style,
                    bottom: getScaledPosition(),
                    right: getScaledPosition(),
                    transformOrigin: 'bottom right',
                };
            default:
                return {
                    ...style,
                    top: getScaledPosition(),
                    left: getScaledPosition(),
                    transformOrigin: 'top left',
                };
        }
    };

    // Create a style object for the badge background container
    const getBadgeBackgroundStyle = () => {
        // Get values with defaults if not specified
        const backgroundColor = settings.background_color || '#000000';
        const backgroundOpacity = settings.background_transparency !== undefined ? settings.background_transparency : 0.8;
        const borderRadius = `${settings.border_radius || 4}px`;
        const borderWidth = `${settings.border_width || 1}px`;
        const borderColor = settings.border_color || '#ffffff';
        const borderOpacity = settings.border_transparency !== undefined ? settings.border_transparency : 0.8;
        const zIndex = settings.z_index || 1;
        const size = settings.size || 100; // Size as percentage (100% = original size)
        
        // Convert HEX color to RGBA for transparency
        const hexToRgba = (hex: string, alpha: number) => {
            // Remove # if present
            hex = hex.replace('#', '');
            
            // Parse RGB values
            const r = parseInt(hex.substring(0, 2), 16);
            const g = parseInt(hex.substring(2, 4), 16);
            const b = parseInt(hex.substring(4, 6), 16);
            
            // Return rgba string
            return `rgba(${r}, ${g}, ${b}, ${alpha})`;
        };
        
        // Create base style
        let style: React.CSSProperties = {
            backgroundColor: hexToRgba(backgroundColor, backgroundOpacity),
            borderRadius: borderRadius,
            borderWidth: borderWidth,
            borderStyle: 'solid',
            borderColor: hexToRgba(borderColor, borderOpacity),
            padding: '8px',
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            zIndex: zIndex,
            // Apply transform scale based on size percentage
            transform: `scale(${size / 100})`,
            // Note: transformOrigin is set in the position style
        };
        
        // Add shadow if enabled
        if (settings.shadow_toggle) {
            const shadowColor = settings.shadow_color || '#000000';
            const shadowBlurRadius = `${settings.shadow_blur_radius || 5}px`;
            const shadowOffsetX = `${settings.shadow_offset_x || 2}px`;
            const shadowOffsetY = `${settings.shadow_offset_y || 2}px`;
            
            style.boxShadow = `${shadowOffsetX} ${shadowOffsetY} ${shadowBlurRadius} ${hexToRgba(shadowColor, 0.5)}`;
        }
        
        return style;
    };

    // Position style for the container
    const positionStyle = getBadgePosition();
    // Background style for the container
    const backgroundStyle = getBadgeBackgroundStyle();
    
    // Combine both styles
    const containerStyle = {
        ...positionStyle,
        ...backgroundStyle,
    };

    return (
        <Card>
            <CardHeader>
                <CardTitle className="text-xl font-semibold">Preview</CardTitle>
                <p className="text-sm text-muted-foreground">Preview Your Changes Here</p>
                <p className="text-xs text-muted-foreground">Current Image: 1000px x 1500px</p>
            </CardHeader>
            <CardContent className="flex items-center justify-center">
                <div className="relative" style={{ width: '100%', maxWidth: '1000px' }}>
                    {/* Poster Image */}
                    <img
                        src={previewImage}
                        alt="Poster Preview"
                        width={1000}
                        height={1500}
                        className="rounded-md border border-gray-300"
                        style={{
                            width: '100%',
                            height: 'auto',
                            objectFit: 'contain',
                        }}
                    />
                    
                    {/* Resolution Badge Container with Background */}
                    <div style={containerStyle}>
                        <img
                            src={imagePath}
                            alt={`Resolution: ${selectedResolution}`}
                            style={{
                                maxWidth: '100%',
                                height: 'auto',
                            }}
                        />
                    </div>
                    
                    {/* Toggle Button */}
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={togglePreviewImage}
                        className="absolute top-2 right-2 bg-white/50 text-black hover:bg-white/70 backdrop-blur-md"
                    >
                        Toggle Poster
                    </Button>
                </div>
            </CardContent>
        </Card>
    );
};

export default PreviewCard;