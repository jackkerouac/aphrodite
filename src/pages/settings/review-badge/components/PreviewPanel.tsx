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
      padding: '8px',
      ...getBadgePosition()
    };
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
    // Convert hex to rgba for text
    const textR = parseInt(settings.text_color.slice(1, 3), 16);
    const textG = parseInt(settings.text_color.slice(3, 5), 16);
    const textB = parseInt(settings.text_color.slice(5, 7), 16);

    return {
      display: 'flex', 
      alignItems: 'center',
      color: `rgba(${textR}, ${textG}, ${textB}, ${1 - settings.text_transparency})`,
      fontFamily: settings.font_family,
      fontSize: `${settings.font_size}px`,
      fontWeight: settings.font_weight,
    };
  };

  // Get logo style
  const getLogoStyle = () => {
    const marginKey = settings.logo_position === 'left' ? 'marginRight' :
                      settings.logo_position === 'right' ? 'marginLeft' :
                      settings.logo_position === 'top' ? 'marginBottom' : 'marginTop';
    
    return {
      width: `${settings.logo_size}px`,
      height: `${settings.logo_size}px`,
      objectFit: 'contain' as 'contain',
      [marginKey]: '4px',
    };
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
      const formattedScore = formatScore(score, settings.score_format);
      
      const badgeStyle = getBadgeStyle();
      const logoStyle = getLogoStyle();
      
      // For top/bottom logo positioning, wrap in a column flex container
      const wrapperStyle = settings.logo_position === 'top' || settings.logo_position === 'bottom' 
        ? { display: 'flex', flexDirection: 'column', alignItems: 'center' } 
        : {};
      
      return (
        <div key={source} style={badgeStyle}>
          <div style={wrapperStyle as React.CSSProperties}>
            {settings.show_logo && settings.logo_position === 'left' && (
              <img src={logo} alt={`${source} logo`} style={logoStyle} />
            )}
            
            {settings.show_logo && settings.logo_position === 'top' && (
              <img src={logo} alt={`${source} logo`} style={logoStyle} />
            )}
            
            <span>{formattedScore}</span>
            
            {settings.show_logo && settings.logo_position === 'right' && (
              <img src={logo} alt={`${source} logo`} style={logoStyle} />
            )}
            
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
            <p>Position: {settings.position}</p>
            <p>Layout: {settings.badge_layout}</p>
            <p>Displayed Sources: {settings.display_sources.join(', ')}</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default PreviewPanel;
