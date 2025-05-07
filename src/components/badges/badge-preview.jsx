import React from 'react';
import { cn } from '../../lib/utils';
import { Card, CardContent } from '../ui/card';
import { H3 } from '../ui/typography';

/**
 * BadgePreview Component
 * 
 * Displays a preview of how badges will appear on media posters
 * Based on the Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {Object} props.settings - Badge display settings
 * @param {string} props.type - Type of badge (audio, resolution, review)
 * @param {string} props.imageUrl - Optional background image URL
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} BadgePreview component
 */
export const BadgePreview = ({
  settings = {},
  type = 'audio',
  imageUrl,
  className = "",
  ...props
}) => {
  // Get badge content based on type
  const getBadgeContent = () => {
    switch (type) {
      case 'audio':
        return {
          text: 'DOLBY ATMOS',
          style: { color: '#00E5FF' }
        };
      case 'resolution':
        return {
          text: '4K',
          style: { color: '#22C55E' }
        };
      case 'review':
        return {
          text: 'IMDb 8.5',
          style: {}
        };
      default:
        return {
          text: 'BADGE',
          style: {}
        };
    }
  };
  
  // Calculate badge position based on settings
  const getBadgePosition = () => {
    const { position = 'top-right' } = settings;
    
    const positionMap = {
      'top-left': { top: settings.margin || 16, left: settings.margin || 16 },
      'top-center': { top: settings.margin || 16, left: '50%', transform: 'translateX(-50%)' },
      'top-right': { top: settings.margin || 16, right: settings.margin || 16 },
      'center-left': { top: '50%', left: settings.margin || 16, transform: 'translateY(-50%)' },
      'center': { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' },
      'center-right': { top: '50%', right: settings.margin || 16, transform: 'translateY(-50%)' },
      'bottom-left': { bottom: settings.margin || 16, left: settings.margin || 16 },
      'bottom-center': { bottom: settings.margin || 16, left: '50%', transform: 'translateX(-50%)' },
      'bottom-right': { bottom: settings.margin || 16, right: settings.margin || 16 },
    };
    
    return positionMap[position] || positionMap['top-right'];
  };
  
  // Get badge content
  const badgeContent = getBadgeContent();
  
  // Get badge position
  const badgePosition = getBadgePosition();
  
  // Default settings if not provided
  const defaultSettings = {
    size: 100, // percentage of original size
    margin: 16, // px
    background_color: '#000000',
    background_transparency: 0.2,
    border_radius: 6, // px
    border_width: 1, // px
    border_color: '#FFFFFF',
    border_transparency: 0.5,
    shadow_toggle: true,
    shadow_color: 'rgba(0, 0, 0, 0.5)',
    shadow_blur_radius: 10, // px
    shadow_offset_x: 0, // px
    shadow_offset_y: 4, // px
    z_index: 1,
  };
  
  // Merge default settings with provided settings
  const mergedSettings = { ...defaultSettings, ...settings };
  
  // Calculate size based on settings
  const calculateSize = () => {
    const baseSize = 14; // base font size in px
    return (baseSize * mergedSettings.size) / 100;
  };
  
  return (
    <Card className={cn("", className)} {...props}>
      <CardContent>
        <H3 className="mb-default">Preview</H3>
        
        <div 
          className="relative w-full aspect-[2/3] rounded-lg overflow-hidden bg-bg-dark"
          style={{
            backgroundImage: imageUrl ? `url(${imageUrl})` : 'none',
            backgroundSize: 'cover',
            backgroundPosition: 'center',
          }}
        >
          {/* Placeholder image if no imageUrl */}
          {!imageUrl && (
            <div className="absolute inset-0 flex items-center justify-center">
              <span className="text-neutral opacity-50">Poster Preview</span>
            </div>
          )}
          
          {/* Badge element */}
          <div
            className="badge-appear absolute"
            style={{
              ...badgePosition,
              backgroundColor: `${mergedSettings.background_color}${Math.round(mergedSettings.background_transparency * 255).toString(16).padStart(2, '0')}`,
              borderRadius: `${mergedSettings.border_radius}px`,
              borderWidth: `${mergedSettings.border_width}px`,
              borderStyle: 'solid',
              borderColor: `${mergedSettings.border_color}${Math.round(mergedSettings.border_transparency * 255).toString(16).padStart(2, '0')}`,
              padding: '4px 8px',
              fontSize: `${calculateSize()}px`,
              boxShadow: mergedSettings.shadow_toggle ? 
                `${mergedSettings.shadow_offset_x}px ${mergedSettings.shadow_offset_y}px ${mergedSettings.shadow_blur_radius}px ${mergedSettings.shadow_color}` : 
                'none',
              zIndex: mergedSettings.z_index,
              fontWeight: 'bold',
              fontFamily: 'JetBrains Mono, monospace',
              ...badgeContent.style,
            }}
          >
            {badgeContent.text}
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

/**
 * AudioBadgePreview Component
 * 
 * Specialized badge preview for audio badges
 * 
 * @param {Object} props - Component props
 * @param {Object} props.settings - Badge display settings
 * @param {string} props.codecType - Audio codec type (e.g., 'DOLBY ATMOS', 'DTS-HD')
 * @param {string} props.imageUrl - Optional background image URL
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} AudioBadgePreview component
 */
export const AudioBadgePreview = ({
  settings = {},
  codecType = 'DOLBY ATMOS',
  imageUrl,
  className = "",
  ...props
}) => {
  // Get style based on codec type
  const getCodecStyle = () => {
    switch (codecType.toUpperCase()) {
      case 'DOLBY ATMOS':
        return { color: '#00E5FF' };
      case 'DTS-HD':
        return { color: '#FF8C00' };
      case 'DOLBY DIGITAL':
        return { color: '#FF4081' };
      default:
        return { color: '#FFFFFF' };
    }
  };
  
  return (
    <BadgePreview
      settings={settings}
      type="audio"
      imageUrl={imageUrl}
      className={className}
      badgeContent={{
        text: codecType.toUpperCase(),
        style: getCodecStyle(),
      }}
      {...props}
    />
  );
};

/**
 * ResolutionBadgePreview Component
 * 
 * Specialized badge preview for resolution badges
 * 
 * @param {Object} props - Component props
 * @param {Object} props.settings - Badge display settings
 * @param {string} props.resolution - Resolution type (e.g., '4K', '1080p')
 * @param {string} props.imageUrl - Optional background image URL
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} ResolutionBadgePreview component
 */
export const ResolutionBadgePreview = ({
  settings = {},
  resolution = '4K',
  imageUrl,
  className = "",
  ...props
}) => {
  // Get style based on resolution
  const getResolutionStyle = () => {
    switch (resolution.toUpperCase()) {
      case '4K':
      case '2160P':
        return { color: '#22C55E' };
      case '1080P':
        return { color: '#3B82F6' };
      case '720P':
        return { color: '#F59E0B' };
      case 'SD':
        return { color: '#9CA3AF' };
      default:
        return { color: '#FFFFFF' };
    }
  };
  
  return (
    <BadgePreview
      settings={settings}
      type="resolution"
      imageUrl={imageUrl}
      className={className}
      badgeContent={{
        text: resolution.toUpperCase(),
        style: getResolutionStyle(),
      }}
      {...props}
    />
  );
};
