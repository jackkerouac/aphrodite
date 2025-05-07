import * as React from "react";
import { cn } from "../../lib/utils";

/**
 * Input Component
 * 
 * Text input field with styling based on Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {boolean} props.error - Whether the input has an error
 * @param {boolean} props.success - Whether the input has a success state
 * @returns {JSX.Element} Input component
 */
const Input = React.forwardRef(
  ({ className, error, success, type, ...props }, ref) => {
    let statusStyles = "";
    if (error) statusStyles = "border-error focus:ring-error";
    if (success) statusStyles = "border-success focus:ring-success";
    
    return (
      <input
        type={type || "text"}
        className={cn(
          "h-12 rounded-lg border border-neutral bg-white dark:bg-[#2E2E3E] px-3",
          "focus:outline-none focus:ring-2 focus:ring-primary-purple",
          "placeholder:text-neutral text-dark dark:text-[#F3F4F6]",
          "disabled:cursor-not-allowed disabled:opacity-50",
          statusStyles,
          className
        )}
        ref={ref}
        style={{
          color: '#1F2937', // Enforce darker text color in light mode
          ...(props.style || {})
        }}
        {...props}
      />
    );
  }
);

Input.displayName = "Input";

export { Input };
