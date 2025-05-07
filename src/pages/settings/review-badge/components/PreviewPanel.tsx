import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { ReviewBadgeSettings } from '../hooks/useReviewBadgeSettings';
import { formatScore } from '../constants';

interface ReviewData {
  [key: string]: {
    score: number;
    logo: string;
  };
}

interface PreviewPanelProps {
  previewImage: string;
  togglePreviewImage: () => void;
  settings: ReviewBadgeSettings;
  reviewData: ReviewData;
}

const PreviewPanel: React.FC<PreviewPanelProps> = ({
  previewImage,
  togglePreviewImage,
  settings,
  reviewData
}) => {
  // Generate the badge position based on settings
  const getBadgePosition = () => {
    const position = settings.position || 'top-left';
    
    // Position mapping
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
        return { top: `${settings.margin}px`, left: `${settings.margin}px` };
    }
  };

  // Get container style for the entire badges group
  const getContainerStyle = () => {
    // Apply shadow if enabled
    let shadow = '';
    if (settings.shadow_toggle) {
      const shadowColor = settings.shadow_color || '#000000';
      // Convert hex to rgba to include transparency
      const r = parseInt(shadowColor.slice(1, 3), 16);
      const g = parseInt(shadowColor.slice(3, 5), 16);
      const b = parseInt(shadowColor.slice(5, 7), 16);
      shadow = `${settings.shadow_offset_x || 0}px ${settings.shadow_offset_y || 0}px ${settings.shadow_blur_radius || 0}px rgba(${r}, ${g}, ${b}, 1)`;
    }

    // Ensure background_color and border_color are not null
    const bgColor = settings.background_color || '#000000';
    const borderColor = settings.border_color || '#ffffff';

    // Convert hex to rgba for background and border
    const bgR = parseInt(bgColor.slice(1, 3), 16);
    const bgG = parseInt(bgColor.slice(3, 5), 16);
    const bgB = parseInt(bgColor.slice(5, 7), 16);
    
    const borderR = parseInt(borderColor.slice(1, 3), 16);
    const borderG = parseInt(borderColor.slice(3, 5), 16);
    const borderB = parseInt(borderColor.slice(5, 7), 16);

    // Get position-based styles
    const positionStyles = getBadgePosition();
    // Apply scaling factor based on size setting
    const scaleFactor = settings.size / 100;
    
    // Handle transform property - combine scale with any existing transforms
    let transformValue = `scale(${scaleFactor})`;
    if (positionStyles.transform) {
      transformValue = `${positionStyles.transform} scale(${scaleFactor})`;
      // Remove the transform from positionStyles to avoid duplication
      delete positionStyles.transform;
    }

    return {
      position: 'absolute',
      zIndex: settings.z_index,
      boxShadow: shadow || 'none',
      backgroundColor: `rgba(${bgR}, ${bgG}, ${bgB}, ${settings.background_transparency || 0.8})`,
      borderRadius: `${settings.border_radius || 4}px`,
      border: `${settings.border_width || 1}px solid rgba(${borderR}, ${borderG}, ${borderB}, ${settings.border_transparency || 0.8})`,
      padding: '8px',
      transform: transformValue,
      transformOrigin: getTransformOrigin(settings.position),
      ...positionStyles
    };
  };

  // Helper function to determine transform-origin based on badge position
  const getTransformOrigin = (position: string) => {
    switch (position) {
      case 'top-left': return 'top left';
      case 'top-center': return 'top center';
      case 'top-right': return 'top right';
      case 'bottom-left': return 'bottom left';
      case 'bottom-center': return 'bottom center';
      case 'bottom-right': return 'bottom right';
      default: return 'top left';
    }
  };

  // Get badge group style (horizontal or vertical)
  const getBadgeGroupStyle = () => {
    return {
      display: 'flex',
      flexDirection: settings.badge_layout === 'vertical' ? 'column' : 'row',
      gap: `${settings.spacing}px`,
    };
  };

  // Get single badge style
  const getBadgeStyle = () => {
    // Ensure text_color is not null
    const textColor = settings.text_color || '#ffffff';
    
    // Convert hex to rgba for text
    const textR = parseInt(textColor.slice(1, 3), 16);
    const textG = parseInt(textColor.slice(3, 5), 16);
    const textB = parseInt(textColor.slice(5, 7), 16);

    // Apply scaling factor to font size
    const scaleFactor = settings.size / 100;

    return {
      display: 'flex', 
      alignItems: 'center',
      color: `rgba(${textR}, ${textG}, ${textB}, ${1 - (settings.text_transparency || 0)})`,
      fontFamily: settings.font_family || 'Inter',
      fontSize: `${settings.font_size || 16}px`, // Font size is scaled at the container level
      fontWeight: settings.font_weight || 600,
    };
  };

  // Get logo style
  const getLogoStyle = (source: string) => {
    // Base style for all logos
    const style: React.CSSProperties = {
      maxWidth: `${settings.logo_size}px`,
      maxHeight: `${settings.logo_size}px`,
      objectFit: 'contain' as 'contain',
      display: 'block', // Helps with alignment
    };
    
    // Only add spacing if it's greater than 0
    if (settings.logoTextSpacing > 0) {
      const marginKey = settings.logo_position === 'top' ? 'marginBottom' : 'marginTop';
      style[marginKey] = `${settings.logoTextSpacing}px`;
    }

    // Specific adjustments for certain logos to improve centering
    if (source === 'RottenTomatoes') {
      style.margin = '0 auto'; // Center horizontally
    }
    
    if (source === 'Metacritic') {
      style.margin = '0 auto'; // Center horizontally
    }
    
    return style;
  };

  // Create a badge for each enabled source
  const renderBadges = () => {
    const visibleSources = settings.display_sources || [];
    
    // Sort sources according to the source_order setting
    const sortedSources = [...visibleSources].sort((a, b) => {
      const aIndex = settings.source_order.indexOf(a);
      const bIndex = settings.source_order.indexOf(b);
      return aIndex - bIndex;
    });

    return sortedSources.map(source => {
      if (!reviewData[source]) return null;
      
      const { score, logo } = reviewData[source];
      const formattedScore = formatScore(score, settings.score_format, source);
      
      const badgeStyle = getBadgeStyle();
      const logoStyle = getLogoStyle(source);
      
      // For logo positioning, use a column flex container with no padding/margin
      const wrapperStyle = { 
        display: 'flex', 
        flexDirection: 'column', 
        alignItems: 'center',
        justifyContent: 'center',
        padding: 0,
        margin: 0,
        width: '100%' // Ensure full width for better centering
      };
      
      return (
        <div key={source} style={badgeStyle}>
          <div style={wrapperStyle as React.CSSProperties}>
            {settings.show_logo && settings.logo_position === 'top' && (
              <img src={logo} alt={`${source} logo`} style={logoStyle} />
            )}
            
            <span style={{ margin: 0, padding: 0, textAlign: 'center', display: 'block', width: '100%' }}>{formattedScore}</span>
            
            {settings.show_logo && settings.logo_position === 'bottom' && (
              <img src={logo} alt={`${source} logo`} style={logoStyle} />
            )}
          </div>
        </div>
      );
    });
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
            
            {/* Review Badges */}
            <div style={getContainerStyle()}>
              <div style={getBadgeGroupStyle()}>
                {renderBadges()}
              </div>
            </div>
          </div>
          
          {/* Toggle Preview Button */}
          <Button onClick={togglePreviewImage} variant="outline" className="w-full">
            Toggle Dark/Light Preview
          </Button>

          {/* Badge Information */}
          <div className="text-sm text-muted-foreground">
            <p>Position: {settings.position || 'top-right'}</p>
            <p>Layout: {settings.badge_layout || 'horizontal'}</p>
            <p>Displayed Sources: {Array.isArray(settings.display_sources) && settings.display_sources.length > 0 ? settings.display_sources.join(', ') : 'None'}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PreviewPanel;
