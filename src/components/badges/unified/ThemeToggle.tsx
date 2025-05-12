import React, { useState } from 'react';
import { Switch } from '@/components/ui/switch';
import { Label } from '@/components/ui/label';
import { Sun, Moon } from 'lucide-react';

interface ThemeToggleProps {
  isDarkMode: boolean;
  onToggle: (isDarkMode: boolean) => void;
  className?: string;
}

/**
 * Toggle component for switching between light and dark preview modes
 */
const ThemeToggle: React.FC<ThemeToggleProps> = ({
  isDarkMode,
  onToggle,
  className = ''
}) => {
  return (
    <div className={`flex items-center space-x-2 ${className}`}>
      <Sun className={`h-4 w-4 ${isDarkMode ? 'text-gray-400' : 'text-yellow-500'}`} />
      <Switch
        id="theme-toggle"
        checked={isDarkMode}
        onCheckedChange={onToggle}
      />
      <Label htmlFor="theme-toggle" className="flex items-center cursor-pointer">
        <Moon className={`h-4 w-4 mr-2 ${isDarkMode ? 'text-blue-400' : 'text-gray-400'}`} />
        {isDarkMode ? 'Dark Mode' : 'Light Mode'}
      </Label>
    </div>
  );
};

export default ThemeToggle;
