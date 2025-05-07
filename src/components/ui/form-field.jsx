import React from 'react';
import { cn } from '../../lib/utils';
import { Label } from './typography';

/**
 * FormField Component
 * 
 * A standardized form field layout with label and description
 * Based on the Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {string} props.label - Field label
 * @param {string} props.description - Optional field description
 * @param {string} props.htmlFor - ID for the input field
 * @param {boolean} props.required - Whether the field is required
 * @param {React.ReactNode} props.children - Form field content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} FormField component
 */
export const FormField = ({
  label,
  description,
  htmlFor,
  required = false,
  children,
  className = "",
  ...props
}) => {
  return (
    <div className={cn("mb-default", className)} {...props}>
      {label && (
        <Label 
          htmlFor={htmlFor}
          className="mb-micro flex items-center gap-1"
        >
          {label}
          {required && (
            <span className="text-error">*</span>
          )}
        </Label>
      )}
      
      {children}
      
      {description && (
        <p className="mt-micro text-body-small text-neutral">
          {description}
        </p>
      )}
    </div>
  );
};

/**
 * FormSection Component
 * 
 * A section container for form fields
 * 
 * @param {Object} props - Component props
 * @param {string} props.title - Section title
 * @param {string} props.description - Optional section description
 * @param {React.ReactNode} props.children - Section content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} FormSection component
 */
export const FormSection = ({
  title,
  description,
  children,
  className = "",
  ...props
}) => {
  return (
    <div className={cn("mb-section", className)} {...props}>
      {title && (
        <h3 className="text-h3 font-medium mb-small">
          {title}
        </h3>
      )}
      
      {description && (
        <p className="text-body text-neutral mb-default">
          {description}
        </p>
      )}
      
      <div className="space-y-default">
        {children}
      </div>
    </div>
  );
};

/**
 * FormRow Component
 * 
 * A row layout for form fields
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Row content
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} FormRow component
 */
export const FormRow = ({
  children,
  className = "",
  ...props
}) => {
  return (
    <div 
      className={cn(
        "grid grid-cols-1 gap-default md:grid-cols-2 lg:grid-cols-3",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};

/**
 * FormActions Component
 * 
 * A container for form action buttons
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Action buttons
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} FormActions component
 */
export const FormActions = ({
  children,
  className = "",
  ...props
}) => {
  return (
    <div 
      className={cn(
        "flex flex-wrap items-center justify-end gap-small mt-section pt-small",
        "border-t border-bg-light dark:border-[#3A3559]",
        className
      )}
      {...props}
    >
      {children}
    </div>
  );
};
