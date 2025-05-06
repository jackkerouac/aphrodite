import React from 'react';

interface PosterBadgeProps {
  type: 'audio' | 'resolution' | 'review';
  position: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  value: string;
  theme: 'light' | 'dark';
}

export const PosterBadge = ({ type, position, value, theme }: PosterBadgeProps) => {
  // Position classes
  const positionClasses = {
    'top-left': 'top-2 left-2',
    'top-right': 'top-2 right-2',
    'bottom-left': 'bottom-2 left-2',
    'bottom-right': 'bottom-2 right-2',
  };

  // Type-specific styles
  const typeStyles = {
    audio: {
      light: 'bg-blue-100 text-blue-800 border-blue-300',
      dark: 'bg-blue-900/70 text-blue-100 border-blue-700',
      icon: '🔊',
    },
    resolution: {
      light: 'bg-green-100 text-green-800 border-green-300',
      dark: 'bg-green-900/70 text-green-100 border-green-700',
      icon: '📽️',
    },
    review: {
      light: 'bg-yellow-100 text-yellow-800 border-yellow-300',
      dark: 'bg-yellow-900/70 text-yellow-100 border-yellow-700',
      icon: '⭐',
    },
  };

  // Determine the styles based on type and theme
  const styles = typeStyles[type][theme];

  return (
    <div 
      className={`absolute ${positionClasses[position]} rounded-md px-2 py-1 text-xs font-medium flex items-center border ${styles}`}
    >
      <span className="mr-1">{typeStyles[type].icon}</span> {value}
    </div>
  );
};
