import * as React from "react";
import { cn } from "../../lib/utils";

/**
 * Card Component
 * 
 * Main container for card-based UI elements
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Card content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Card component
 */
const Card = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "bg-white dark:bg-slate-950 rounded-xl p-4 shadow border border-slate-200 dark:border-slate-800 hover:scale-[1.01] hover:shadow-md transition-all duration-200",
      className
    )}
    {...props}
  />
));
Card.displayName = "Card";

/**
 * CardHeader Component
 * 
 * Header section of a card, typically contains title and description
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - CardHeader content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} CardHeader component
 */
const CardHeader = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-2", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

/**
 * CardTitle Component
 * 
 * Title for a card
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - CardTitle content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} CardTitle component
 */
const CardTitle = React.forwardRef(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-h3 font-semibold text-dark dark:text-[#F3F4F6]",
      className
    )}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

/**
 * CardDescription Component
 * 
 * Description for a card
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - CardDescription content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} CardDescription component
 */
const CardDescription = React.forwardRef(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-body text-neutral dark:text-[#A3A3A3]", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

/**
 * CardContent Component
 * 
 * Main content container for a card
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - CardContent children
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} CardContent component
 */
const CardContent = React.forwardRef(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-2 pt-0", className)} {...props} />
));
CardContent.displayName = "CardContent";

/**
 * CardFooter Component
 * 
 * Footer section of a card, typically contains actions
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - CardFooter content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} CardFooter component
 */
const CardFooter = React.forwardRef(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-2 pt-0", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
  CardContent,
  CardFooter
};
