import React from 'react';
import { cn } from '../../lib/utils';
import { Moon, Sun } from 'lucide-react';
import { useTheme } from '../theme-provider';

/**
 * DarkModeToggle Component
 * 
 * A toggle button for switching between light and dark mode
 * Based on the Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} DarkModeToggle component
 */
export const DarkModeToggle = ({
  className = "",
  ...props
}) => {
  const { theme, setTheme } = useTheme();
  const isDarkMode = theme === 'dark';
  
  const toggleTheme = () => {
    setTheme(isDarkMode ? 'light' : 'dark');
  };
  
  return (
    <button
      type="button"
      onClick={toggleTheme}
      className={cn(
        "w-10 h-10 rounded-lg transition-colors duration-200",
        "flex items-center justify-center",
        "bg-bg-light hover:bg-secondary-lilac",
        "dark:bg-[#2A2540] dark:hover:bg-[#3A3559]",
        "focus:outline-none focus:ring-2 focus:ring-secondary-purple",
        "btn-press",
        className
      )}
      aria-label={isDarkMode ? "Switch to light mode" : "Switch to dark mode"}
      {...props}
    >
      {isDarkMode ? (
        <Sun className="h-5 w-5 text-white" />
      ) : (
        <Moon className="h-5 w-5 text-primary-purple" />
      )}
    </button>
  );
};

/**
 * DarkModeToggleWithLabel Component
 * 
 * A dark mode toggle with a label
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} DarkModeToggleWithLabel component
 */
export const DarkModeToggleWithLabel = ({
  className = "",
  ...props
}) => {
  const { theme } = useTheme();
  const isDarkMode = theme === 'dark';
  
  return (
    <div className={cn("flex items-center gap-small", className)} {...props}>
      <DarkModeToggle />
      <span className="text-body font-medium">
        {isDarkMode ? 'Dark Mode' : 'Light Mode'}
      </span>
    </div>
  );
};
