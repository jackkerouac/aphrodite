"use client"

import * as React from "react"
import * as TooltipPrimitive from "@radix-ui/react-tooltip"

import { cn } from "../../lib/utils"

/**
 * TooltipProvider Component
 * 
 * Provider for tooltips with configurable delay
 * 
 * @param {Object} props - Component props
 * @param {number} props.delayDuration - Delay before showing tooltip (in ms)
 * @returns {JSX.Element} TooltipProvider component
 */
function TooltipProvider({
  delayDuration = 300,
  ...props
}) {
  return (<TooltipPrimitive.Provider data-slot="tooltip-provider" delayDuration={delayDuration} {...props} />);
}

/**
 * Tooltip Component
 * 
 * Root component for tooltips
 * 
 * @param {Object} props - Component props
 * @returns {JSX.Element} Tooltip component
 */
function Tooltip({
  ...props
}) {
  return (
    <TooltipProvider>
      <TooltipPrimitive.Root data-slot="tooltip" {...props} />
    </TooltipProvider>
  );
}

/**
 * TooltipTrigger Component
 * 
 * Element that triggers the tooltip
 * 
 * @param {Object} props - Component props
 * @returns {JSX.Element} TooltipTrigger component
 */
function TooltipTrigger({
  ...props
}) {
  return <TooltipPrimitive.Trigger data-slot="tooltip-trigger" {...props} />;
}

/**
 * TooltipContent Component
 * 
 * Content displayed in the tooltip
 * Based on the Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {string} props.className - Additional CSS classes
 * @param {number} props.sideOffset - Offset from trigger element in pixels
 * @param {React.ReactNode} props.children - Tooltip content
 * @returns {JSX.Element} TooltipContent component
 */
function TooltipContent({
  className,
  sideOffset = 4,
  children,
  ...props
}) {
  return (
    <TooltipPrimitive.Portal>
      <TooltipPrimitive.Content
        data-slot="tooltip-content"
        sideOffset={sideOffset}
        className={cn(
          "bg-primary-purple dark:bg-accent-indigo text-primary-white",
          "animate-in fade-in-0 zoom-in-95 data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=closed]:zoom-out-95", 
          "data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2", 
          "z-50 w-fit rounded-lg px-3 py-1.5 text-body-small shadow-md",
          "transition-all duration-200",
          className
        )}
        {...props}>
        {children}
        <TooltipPrimitive.Arrow
          className="fill-primary-purple dark:fill-accent-indigo z-50 size-2.5 translate-y-[calc(-50%_-_2px)] rotate-45 rounded-[2px]" />
      </TooltipPrimitive.Content>
    </TooltipPrimitive.Portal>
  );
}

export { Tooltip, TooltipTrigger, TooltipContent, TooltipProvider }
