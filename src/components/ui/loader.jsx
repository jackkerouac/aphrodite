import React from 'react';
import { cn } from '../../lib/utils';

/**
 * Loader Component
 * 
 * Displays a loading indicator with customizable size and color
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {'sm'|'md'|'lg'} props.size - Size of the loader
 * @param {string} props.color - Color of the loader (tailwind class)
 * @returns {JSX.Element} Loader component
 */
export const Loader = ({
  className = "",
  size = "md",
  color = "bg-secondary-purple",
  ...props
}) => {
  const sizeClasses = {
    sm: "h-4 w-4",
    md: "h-6 w-6",
    lg: "h-8 w-8"
  };

  return (
    <div
      className={cn(
        "loader rounded-full", 
        sizeClasses[size], 
        color,
        className
      )}
      {...props}
    />
  );
};

/**
 * SpinLoader Component
 * 
 * Displays a spinning loading indicator
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {'sm'|'md'|'lg'} props.size - Size of the loader
 * @param {string} props.color - Color of the loader (tailwind class)
 * @returns {JSX.Element} SpinLoader component
 */
export const SpinLoader = ({
  className = "",
  size = "md",
  color = "border-secondary-purple",
  ...props
}) => {
  const sizeClasses = {
    sm: "h-4 w-4 border-2",
    md: "h-6 w-6 border-2",
    lg: "h-8 w-8 border-3"
  };

  return (
    <div
      className={cn(
        "rotate rounded-full border-t-transparent",
        sizeClasses[size],
        color,
        className
      )}
      {...props}
    />
  );
};

/**
 * LoadingDots Component
 * 
 * Displays a loading indicator with three animated dots
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {'sm'|'md'|'lg'} props.size - Size of the dots
 * @param {string} props.color - Color of the dots (tailwind class)
 * @returns {JSX.Element} LoadingDots component
 */
export const LoadingDots = ({
  className = "",
  size = "md",
  color = "bg-secondary-purple",
  ...props
}) => {
  const sizeClasses = {
    sm: "h-1 w-1",
    md: "h-2 w-2",
    lg: "h-3 w-3"
  };

  return (
    <div className={cn("flex items-center space-x-1", className)} {...props}>
      <div className={cn("animate-bounce rounded-full", sizeClasses[size], color, "delay-0")} />
      <div className={cn("animate-bounce rounded-full", sizeClasses[size], color, "delay-150")} />
      <div className={cn("animate-bounce rounded-full", sizeClasses[size], color, "delay-300")} />
    </div>
  );
};

/**
 * ButtonLoader Component
 * 
 * Loading indicator for buttons
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.label - Text to display next to the loader
 * @returns {JSX.Element} ButtonLoader component
 */
export const ButtonLoader = ({
  className = "",
  label = "Loading...",
  ...props
}) => {
  return (
    <div className={cn("flex items-center justify-center gap-2", className)} {...props}>
      <SpinLoader size="sm" className="opacity-70" />
      <span>{label}</span>
    </div>
  );
};
