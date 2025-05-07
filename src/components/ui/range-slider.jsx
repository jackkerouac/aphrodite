import React from 'react';
import { Slider } from './slider';
import { Label, BodySmall } from './typography';
import { cn } from '../../lib/utils';

/**
 * RangeSlider Component
 * 
 * A slider with multiple values and customizable appearance
 * Based on the Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {string} props.label - Slider label
 * @param {Array<number>} props.value - Current values of the slider
 * @param {Function} props.onChange - Callback when values change
 * @param {number} props.min - Minimum value
 * @param {number} props.max - Maximum value
 * @param {number} props.step - Step size
 * @param {boolean} props.showMarkers - Whether to show markers for values
 * @param {string} props.unit - Unit for display (e.g., 'px', '%')
 * @param {boolean} props.disabled - Whether the slider is disabled
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} RangeSlider component
 */
export const RangeSlider = ({
  label,
  value = [0, 100],
  onChange,
  min = 0,
  max = 100,
  step = 1,
  showMarkers = true,
  unit = '',
  disabled = false,
  className = "",
  ...props
}) => {
  const formatValue = (val) => {
    return `${val}${unit}`;
  };
  
  const handleValueChange = (newValue) => {
    if (Array.isArray(newValue) && onChange) {
      onChange(newValue);
    }
  };
  
  return (
    <div className={cn("space-y-small", className)} {...props}>
      {label && (
        <div className="flex items-center justify-between">
          <Label>{label}</Label>
          <div className="flex space-x-small items-center">
            {value.map((val, index) => (
              <span 
                key={index}
                className="text-body-small font-medium text-primary-purple dark:text-accent-indigo"
              >
                {formatValue(val)}
              </span>
            ))}
          </div>
        </div>
      )}
      
      <Slider
        min={min}
        max={max}
        step={step}
        value={value}
        onValueChange={handleValueChange}
        disabled={disabled}
      />
      
      {showMarkers && (
        <div className="flex justify-between mt-1">
          <BodySmall className="text-neutral">{formatValue(min)}</BodySmall>
          <BodySmall className="text-neutral">{formatValue(max)}</BodySmall>
        </div>
      )}
    </div>
  );
};

/**
 * DualRangeSlider Component
 * 
 * A specialized range slider with labels for both ends
 * 
 * @param {Object} props - Component props
 * @param {string} props.label - Slider label
 * @param {Array<number>} props.value - Current values of the slider [min, max]
 * @param {Function} props.onChange - Callback when values change
 * @param {number} props.min - Minimum value
 * @param {number} props.max - Maximum value
 * @param {number} props.step - Step size
 * @param {string} props.minLabel - Label for minimum value
 * @param {string} props.maxLabel - Label for maximum value
 * @param {string} props.unit - Unit for display (e.g., 'px', '%')
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} DualRangeSlider component
 */
export const DualRangeSlider = ({
  label,
  value = [0, 100],
  onChange,
  min = 0,
  max = 100,
  step = 1,
  minLabel = 'Min',
  maxLabel = 'Max',
  unit = '',
  className = "",
  ...props
}) => {
  return (
    <div className={cn("space-y-small", className)} {...props}>
      {label && (
        <Label>{label}</Label>
      )}
      
      <div className="grid grid-cols-2 gap-small">
        <div>
          <BodySmall className="mb-micro">{minLabel}</BodySmall>
          <div className="p-2 bg-bg-light dark:bg-[#2A2540] rounded-md text-center">
            <span className="text-body font-medium">
              {value[0]}{unit}
            </span>
          </div>
        </div>
        
        <div>
          <BodySmall className="mb-micro">{maxLabel}</BodySmall>
          <div className="p-2 bg-bg-light dark:bg-[#2A2540] rounded-md text-center">
            <span className="text-body font-medium">
              {value[1]}{unit}
            </span>
          </div>
        </div>
      </div>
      
      <Slider
        min={min}
        max={max}
        step={step}
        value={value}
        onValueChange={onChange}
      />
    </div>
  );
};
