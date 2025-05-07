import React from 'react';

/**
 * H1 Component - Used for page titles and overlays
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} H1 heading component
 */
export const H1 = ({ children, className = "", ...props }) => (
  <h1 
    className={`text-h1 text-dark dark:text-[#F3F4F6] ${className}`} 
    {...props}
  >
    {children}
  </h1>
);

/**
 * H2 Component - Used for section headers and cards
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} H2 heading component
 */
export const H2 = ({ children, className = "", ...props }) => (
  <h2 
    className={`text-h2 text-dark dark:text-[#F3F4F6] ${className}`} 
    {...props}
  >
    {children}
  </h2>
);

/**
 * H3 Component - Used for subsection headings
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} H3 heading component
 */
export const H3 = ({ children, className = "", ...props }) => (
  <h3 
    className={`text-h3 text-dark dark:text-[#F3F4F6] ${className}`} 
    {...props}
  >
    {children}
  </h3>
);

/**
 * BodyLarge Component - Used for dialog content, modals
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Large body text component
 */
export const BodyLarge = ({ children, className = "", ...props }) => (
  <p 
    className={`text-body-large text-dark dark:text-[#F3F4F6] ${className}`} 
    {...props}
  >
    {children}
  </p>
);

/**
 * Body Component - Used for primary UI content
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Standard body text component
 */
export const Body = ({ children, className = "", ...props }) => (
  <p 
    className={`text-body text-dark dark:text-[#F3F4F6] ${className}`} 
    {...props}
  >
    {children}
  </p>
);

/**
 * BodySmall Component - Used for labels, metadata, table headers
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Small body text component
 */
export const BodySmall = ({ children, className = "", ...props }) => (
  <p 
    className={`text-body-small text-dark dark:text-[#F3F4F6] ${className}`} 
    {...props}
  >
    {children}
  </p>
);

/**
 * CodeText Component - Used for metadata tags, IDs
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Monospace code text component
 */
export const CodeText = ({ children, className = "", ...props }) => (
  <code 
    className={`text-code font-mono text-dark dark:text-[#F3F4F6] ${className}`} 
    {...props}
  >
    {children}
  </code>
);

/**
 * Label Component - Used for form field labels
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.htmlFor - ID of the associated form element
 * @returns {JSX.Element} Form label component
 */
export const Label = ({ children, className = "", htmlFor, ...props }) => (
  <label 
    htmlFor={htmlFor}
    className={`text-body-small font-medium text-dark dark:text-[#F3F4F6] block mb-2 ${className}`} 
    {...props}
  >
    {children}
  </label>
);

/**
 * Subtitle Component - Used for descriptive text under headings
 * @param {Object} props - React props
 * @param {React.ReactNode} props.children - Child elements
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} Subtitle component
 */
export const Subtitle = ({ children, className = "", ...props }) => (
  <p 
    className={`text-body text-neutral dark:text-[#A3A3A3] ${className}`} 
    {...props}
  >
    {children}
  </p>
);
