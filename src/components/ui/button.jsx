import * as React from "react";
import { Slot } from "@radix-ui/react-slot";
import { cva } from "class-variance-authority";
import { cn } from "../../lib/utils";

/**
 * Button component with variants based on the Aphrodite style guide
 */
const buttonVariants = cva(
  "h-12 rounded-lg transition-all duration-150 font-medium text-body-large focus:outline-none focus:ring-2 focus:ring-secondary-purple focus:ring-opacity-50 inline-flex items-center justify-center border border-primary-purple",
  {
    variants: {
      variant: {
        primary: "bg-primary-purple text-primary-white hover:bg-secondary-purple",
        secondary: "border-[1.5px] border-primary-purple text-primary-purple bg-transparent hover:bg-secondary-lilac",
        icon: "w-10 h-10 bg-bg-light text-primary-purple hover:bg-secondary-lilac flex items-center justify-center",
        ghost: "bg-transparent hover:bg-secondary-lilac hover:text-primary-purple",
        link: "text-primary-purple underline-offset-4 hover:underline bg-transparent h-auto p-0",
        destructive: "bg-error text-white hover:bg-error/90",
      },
      size: {
        default: "h-12 px-5",
        sm: "h-10 px-4 text-body",
        lg: "h-14 px-6 text-[18px]",
        icon: "h-10 w-10 p-0",
      },
      disabled: {
        true: "opacity-50 cursor-not-allowed pointer-events-none",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "default",
      disabled: false,
    },
  }
);

/**
 * Button Component
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Button content
 * @param {string} props.className - Additional CSS classes
 * @param {'primary' | 'secondary' | 'icon' | 'ghost' | 'link' | 'destructive'} props.variant - Button style variant
 * @param {'default' | 'sm' | 'lg' | 'icon'} props.size - Button size
 * @param {boolean} props.asChild - Use button as a child wrapper
 * @param {boolean} props.disabled - Whether the button is disabled
 * @returns {JSX.Element} Button component
 */
const Button = React.forwardRef(
  ({ className, variant, size, asChild = false, disabled, ...props }, ref) => {
    const Comp = asChild ? Slot : "button";
    return (
      <Comp
        className={cn(buttonVariants({ variant, size, disabled, className }))}
        ref={ref}
        disabled={disabled}
        {...props}
      />
    );
  }
);

Button.displayName = "Button";

export { Button, buttonVariants };
