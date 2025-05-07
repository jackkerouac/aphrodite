import React from 'react';
import { cn } from '../../lib/utils';
import { Switch } from './switch';
import { Slider } from './slider';
import { ColorPicker } from './color-picker';
import { Label, BodySmall } from './typography';

/**
 * ShadowControl Component
 * 
 * A component for controlling shadow properties of elements
 * Based on the Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {boolean} props.enabled - Whether the shadow is enabled
 * @param {Function} props.onEnabledChange - Callback when enabled state changes
 * @param {string} props.color - Shadow color in hex format
 * @param {Function} props.onColorChange - Callback when color changes
 * @param {number} props.blurRadius - Shadow blur radius in pixels
 * @param {Function} props.onBlurRadiusChange - Callback when blur radius changes
 * @param {number} props.offsetX - Shadow horizontal offset in pixels
 * @param {Function} props.onOffsetXChange - Callback when horizontal offset changes
 * @param {number} props.offsetY - Shadow vertical offset in pixels
 * @param {Function} props.onOffsetYChange - Callback when vertical offset changes
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} ShadowControl component
 */
export const ShadowControl = ({
  enabled = true,
  onEnabledChange,
  color = 'rgba(0, 0, 0, 0.5)',
  onColorChange,
  blurRadius = 10,
  onBlurRadiusChange,
  offsetX = 0,
  onOffsetXChange,
  offsetY = 4,
  onOffsetYChange,
  className = "",
  ...props
}) => {
  // Handle slider value changes
  const handleBlurChange = (value) => {
    if (Array.isArray(value)) {
      onBlurRadiusChange(value[0]);
    } else {
      onBlurRadiusChange(value);
    }
  };
  
  const handleOffsetXChange = (value) => {
    if (Array.isArray(value)) {
      onOffsetXChange(value[0]);
    } else {
      onOffsetXChange(value);
    }
  };
  
  const handleOffsetYChange = (value) => {
    if (Array.isArray(value)) {
      onOffsetYChange(value[0]);
    } else {
      onOffsetYChange(value);
    }
  };
  
  return (
    <div className={cn("space-y-default", className)} {...props}>
      <div className="flex items-center justify-between">
        <Label>Shadow</Label>
        <Switch
          checked={enabled}
          onCheckedChange={onEnabledChange}
        />
      </div>
      
      {enabled && (
        <div className="space-y-small pl-small border-l-2 border-secondary-lilac dark:border-[#3A3559]">
          <div>
            <div className="flex justify-between mb-micro">
              <BodySmall>Color</BodySmall>
            </div>
            <ColorPicker
              value={color}
              onChange={onColorChange}
            />
          </div>
          
          <div>
            <div className="flex justify-between mb-micro">
              <BodySmall>Blur Radius ({blurRadius}px)</BodySmall>
            </div>
            <Slider
              min={0}
              max={30}
              value={[blurRadius]}
              onValueChange={handleBlurChange}
              step={1}
            />
          </div>
          
          <div>
            <div className="flex justify-between mb-micro">
              <BodySmall>Horizontal Offset ({offsetX}px)</BodySmall>
            </div>
            <Slider
              min={-20}
              max={20}
              value={[offsetX]}
              onValueChange={handleOffsetXChange}
              step={1}
            />
          </div>
          
          <div>
            <div className="flex justify-between mb-micro">
              <BodySmall>Vertical Offset ({offsetY}px)</BodySmall>
            </div>
            <Slider
              min={-20}
              max={20}
              value={[offsetY]}
              onValueChange={handleOffsetYChange}
              step={1}
            />
          </div>
          
          <div className="mt-small">
            <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg">
              <div 
                className="w-full h-10 bg-primary-purple dark:bg-accent-indigo rounded-md"
                style={{
                  boxShadow: `${offsetX}px ${offsetY}px ${blurRadius}px ${color}`
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

/**
 * BorderControl Component
 * 
 * A component for controlling border properties of elements
 * 
 * @param {Object} props - Component props
 * @param {number} props.width - Border width in pixels
 * @param {Function} props.onWidthChange - Callback when width changes
 * @param {number} props.radius - Border radius in pixels
 * @param {Function} props.onRadiusChange - Callback when radius changes
 * @param {string} props.color - Border color in hex format
 * @param {Function} props.onColorChange - Callback when color changes
 * @param {number} props.transparency - Border transparency (0-1)
 * @param {Function} props.onTransparencyChange - Callback when transparency changes
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} BorderControl component
 */
export const BorderControl = ({
  width = 1,
  onWidthChange,
  radius = 6,
  onRadiusChange,
  color = '#FFFFFF',
  onColorChange,
  transparency = 0.5,
  onTransparencyChange,
  className = "",
  ...props
}) => {
  // Handle slider value changes
  const handleWidthChange = (value) => {
    if (Array.isArray(value)) {
      onWidthChange(value[0]);
    } else {
      onWidthChange(value);
    }
  };
  
  const handleRadiusChange = (value) => {
    if (Array.isArray(value)) {
      onRadiusChange(value[0]);
    } else {
      onRadiusChange(value);
    }
  };
  
  return (
    <div className={cn("space-y-default", className)} {...props}>
      <Label>Border</Label>
      
      <div className="space-y-small">
        <div>
          <div className="flex justify-between mb-micro">
            <BodySmall>Border Radius ({radius}px)</BodySmall>
          </div>
          <Slider
            min={0}
            max={20}
            value={[radius]}
            onValueChange={handleRadiusChange}
            step={1}
          />
        </div>
        
        <div>
          <div className="flex justify-between mb-micro">
            <BodySmall>Border Width ({width}px)</BodySmall>
          </div>
          <Slider
            min={0}
            max={10}
            value={[width]}
            onValueChange={handleWidthChange}
            step={1}
          />
        </div>
        
        <div className="flex gap-small items-end">
          <div className="flex-1">
            <BodySmall className="mb-micro">Color</BodySmall>
            <ColorPicker
              value={color}
              onChange={onColorChange}
            />
          </div>
          
          <div className="flex-1">
            <BodySmall className="mb-micro">Transparency ({Math.round(transparency * 100)}%)</BodySmall>
            <input
              type="range"
              min="0"
              max="1"
              step="0.01"
              value={transparency}
              onChange={(e) => onTransparencyChange(parseFloat(e.target.value))}
              className={cn(
                "w-full h-1.5 bg-bg-light rounded-full appearance-none cursor-pointer",
                "dark:bg-[#2E2E3E]",
                "[&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4",
                "[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-purple [&::-webkit-slider-thumb]:dark:bg-accent-indigo"
              )}
            />
          </div>
        </div>
        
        <div className="mt-small">
          <div className="p-default bg-bg-light dark:bg-[#2A2540] rounded-lg">
            <div 
              className="w-full h-10 bg-primary-purple dark:bg-accent-indigo"
              style={{
                borderWidth: `${width}px`,
                borderStyle: 'solid',
                borderColor: `${color}${Math.round(transparency * 255).toString(16).padStart(2, '0')}`,
                borderRadius: `${radius}px`,
              }}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
