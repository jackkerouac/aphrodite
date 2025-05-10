import React, { useState, useEffect } from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import apiClient from '@/lib/api-client';
import { AudioBadgeSettings } from '@/pages/settings/audio-badge/hooks/useAudioBadgeSettings';

interface AudioBadgeToggleProps {
  onChange?: (isEnabled: boolean) => void;
  className?: string;
}

const AudioBadgeToggle: React.FC<AudioBadgeToggleProps> = ({ 
  onChange, 
  className = '' 
}) => {
  const [enabled, setEnabled] = useState(true);
  const [settings, setSettings] = useState<AudioBadgeSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const loadSettings = async () => {
      try {
        setIsLoading(true);
        const data = await apiClient.audioBadge.getSettings();
        setSettings(data);
        setIsLoading(false);
      } catch (error) {
        console.error('Error loading audio badge settings:', error);
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
        id="audio-badge-toggle"
        checked={enabled}
        disabled={isLoading}
        onCheckedChange={handleToggle}
      />
      <Label htmlFor="audio-badge-toggle" className="cursor-pointer">
        Audio Badge {isLoading ? '(Loading...)' : ''}
      </Label>
    </div>
  );
};

export default AudioBadgeToggle;