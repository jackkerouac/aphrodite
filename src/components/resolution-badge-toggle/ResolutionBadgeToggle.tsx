import React, { useState, useEffect } from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import apiClient from '@/lib/api-client';
import { ResolutionBadgeSettings } from '@/pages/settings/resolution-badge/hooks/useResolutionBadgeSettings';

interface ResolutionBadgeToggleProps {
  onChange?: (isEnabled: boolean) => void;
  className?: string;
}

const ResolutionBadgeToggle: React.FC<ResolutionBadgeToggleProps> = ({ 
  onChange, 
  className = '' 
}) => {
  const [enabled, setEnabled] = useState(true);
  const [settings, setSettings] = useState<ResolutionBadgeSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true);
        const data = await apiClient.resolutionBadge.getSettings();
        setSettings(data);
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading resolution badge settings:', error);
        setIsLoading(false);
      }
    };

    loadSettings();
  }, []);

  const handleToggle = (value: boolean) => {
    setEnabled(value);
    if (onChange) {
      onChange(value);
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
      <Label htmlFor="resolution-badge-toggle" className="cursor-pointer">
        Resolution Badge {isLoading ? '(Loading...)' : ''}
      </Label>
    </div>
  );
};

export default ResolutionBadgeToggle;