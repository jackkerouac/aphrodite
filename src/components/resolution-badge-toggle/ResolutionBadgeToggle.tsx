import React, { useState, useEffect } from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import apiClient from '@/lib/api-client';
// Import from the settings hook for consistency
import { useResolutionBadgeSettings, ResolutionBadgeSettings } from '@/pages/settings/resolution-badge/hooks/useResolutionBadgeSettings';
import { getSourceImageUrlForResolution } from '@/utils/resolutionUtils';

interface ResolutionBadgeToggleProps {
  onChange?: (isEnabled: boolean) => void;
  className?: string;
  initialEnabled?: boolean;
}

const ResolutionBadgeToggle: React.FC<ResolutionBadgeToggleProps> = ({ 
  onChange, 
  className = '',
  initialEnabled = true
}) => {
  // Use the initialEnabled prop to set the initial state
  const [enabled, setEnabled] = useState(initialEnabled);
  const { settings, loading: isLoading } = useResolutionBadgeSettings();
  const [iconSrc, setIconSrc] = useState<string | undefined>(undefined);
  
  // Set initial state based on settings if available
  useEffect(() => {
    if (settings && settings.resolution_type) {
      // Only load the icon, but don't change the enabled state
      // This ensures we respect the initialEnabled value from props
      
      // Load the icon when settings are available
      const loadIcon = async () => {
        try {
          const imagePath = await getSourceImageUrlForResolution(settings.resolution_type);
          setIconSrc(imagePath);
        } catch (error) {
          console.error('Error loading resolution badge icon:', error);
        }
      };
      
      loadIcon();
    }
  }, [settings]);

  const handleToggle = (value: boolean) => {
    setEnabled(value);
    if (onChange) {
      // Ensure the parent component gets notified of the change
      onChange(value);
      console.log('Resolution badge toggle changed to:', value);
    }
  };

  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Switch
        id="resolution-badge-toggle"
        checked={enabled}
        disabled={isLoading}
        onCheckedChange={handleToggle}
      />
      <div className="flex items-center">
        <Label htmlFor="resolution-badge-toggle" className="cursor-pointer mr-2">
          Resolution Badge {isLoading ? '(Loading...)' : ''}
        </Label>
        {iconSrc && !isLoading && (
          <img 
            src={iconSrc} 
            alt="Resolution badge preview" 
            className="w-6 h-4 object-contain" 
            title={settings?.resolution_type || 'Resolution badge'}
          />
        )}
      </div>
    </div>
  );
};

export default ResolutionBadgeToggle;