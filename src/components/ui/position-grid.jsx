import React from 'react';
import { cn } from '../../lib/utils';

/**
 * PositionGrid Component
 * 
 * A grid of position options used for selecting placement of badges or elements
 * Based on the Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {string} props.value - Currently selected position value
 * @param {Function} props.onChange - Handler for position changes
 * @param {Array} props.options - Array of position options with value and label
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} PositionGrid component
 */
export const PositionGrid = ({ 
  value, 
  onChange, 
  options = [
    { value: 'top-left', label: 'Top Left' },
    { value: 'top-center', label: 'Top Center' },
    { value: 'top-right', label: 'Top Right' },
    { value: 'bottom-left', label: 'Bottom Left' },
    { value: 'bottom-center', label: 'Bottom Center' },
    { value: 'bottom-right', label: 'Bottom Right' },
  ],
  className = "",
  ...props 
}) => {
  // Default grid is 3x2 (top and bottom rows with left, center, right positions)
  const columns = 3;
  
  return (
    <div 
      className={cn(
        `grid grid-cols-${columns} gap-small`,
        className
      )} 
      {...props}
    >
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={cn(
            "h-10 px-3 py-2 rounded-lg text-body font-medium transition-all duration-200",
            "border-2 border-primary-purple dark:border-accent-indigo",
            "focus:outline-none focus:ring-2 focus:ring-secondary-purple",
            value === option.value
              ? "bg-primary-purple text-white dark:bg-accent-indigo"
              : "bg-white hover:bg-secondary-lilac hover:border-primary-purple dark:bg-[#2A2540] dark:hover:bg-[#3A3559]"
          )}
        >
          {option.label}
        </button>
      ))}
    </div>
  );
};

/**
 * PositionBox Component
 * 
 * A simpler 3x3 grid layout for positioning with icons instead of text
 * 
 * @param {Object} props - Component props
 * @param {string} props.value - Currently selected position value
 * @param {Function} props.onChange - Handler for position changes
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} PositionBox component
 */
export const PositionBox = ({ 
  value, 
  onChange, 
  className = "",
  ...props 
}) => {
  const positions = [
    'top-left', 'top-center', 'top-right',
    'center-left', 'center', 'center-right',
    'bottom-left', 'bottom-center', 'bottom-right'
  ];
  
  return (
    <div 
      className={cn(
        "grid grid-cols-3 gap-1 w-fit",
        className
      )} 
      {...props}
    >
      {positions.map((pos) => (
        <button
          key={pos}
          type="button"
          onClick={() => onChange(pos)}
          className={cn(
            "w-10 h-10 rounded-md flex items-center justify-center transition-all duration-200",
            "border-2 border-primary-purple dark:border-accent-indigo",
            "focus:outline-none focus:ring-2 focus:ring-secondary-purple",
            value === pos
              ? "bg-primary-purple dark:bg-accent-indigo" 
              : "bg-white hover:bg-secondary-lilac hover:border-primary-purple dark:bg-[#2A2540] dark:hover:bg-[#3A3559]"
          )}
          aria-label={pos}
        >
          <div 
            className={cn(
              "w-2 h-2 rounded-full",
              value === pos 
                ? "bg-white" 
                : "bg-primary-purple dark:bg-accent-indigo"
            )} 
          />
        </button>
      ))}
    </div>
  );
};
