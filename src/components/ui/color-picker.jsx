import React, { useState, useEffect, useRef } from 'react';
import { cn } from '../../lib/utils';
import { PopoverContent, Popover, PopoverTrigger } from './popover';
import { Input } from './input';
import { Label } from './typography';

/**
 * ColorPicker Component
 * 
 * A color picker component that follows the Aphrodite style guide
 * 
 * @param {Object} props - Component props
 * @param {string} props.value - The current color value in hex format
 * @param {Function} props.onChange - Callback when color changes
 * @param {string} props.label - Label for the color picker
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} ColorPicker component
 */
export const ColorPicker = ({ 
  value = '#FFFFFF', 
  onChange,
  label,
  className = "",
  ...props 
}) => {
  const [hexValue, setHexValue] = useState(value);
  
  // Update local state when value prop changes
  useEffect(() => {
    setHexValue(value);
  }, [value]);
  
  // Pre-defined color palette based on Aphrodite style guide
  const colorPalette = [
    // Primary Colors
    '#4C1D95', '#FDFDFD',
    // Secondary Colors
    '#7C3AED', '#EDE9FE',
    // Accent Colors
    '#8B5CF6', '#06B6D4',
    // Functional Colors
    '#22C55E', '#F59E0B', '#EF4444', '#9CA3AF', '#1F2937',
    // Background Colors
    '#FFFFFF', '#F4F4F5', '#1E1B2E'
  ];
  
  // Ensure hex is valid format
  const handleHexChange = (e) => {
    const newValue = e.target.value;
    setHexValue(newValue);
    
    // Only trigger onChange if it's a valid hex color
    if (/^#[0-9A-F]{6}$/i.test(newValue)) {
      onChange(newValue);
    }
  };
  
  // Handle picker change
  const handlePickerChange = (e) => {
    const newValue = e.target.value;
    setHexValue(newValue);
    onChange(newValue);
  };
  
  // Handle palette selection
  const handlePaletteSelect = (color) => {
    setHexValue(color);
    onChange(color);
  };
  
  return (
    <div className={cn("flex flex-col", className)} {...props}>
      {label && (
        <Label className="mb-2">{label}</Label>
      )}
      
      <Popover>
        <PopoverTrigger asChild>
          <button
            type="button"
            className={cn(
              "w-12 h-12 rounded-lg border border-neutral",
              "focus:outline-none focus:ring-2 focus:ring-secondary-purple"
            )}
            style={{ backgroundColor: hexValue }}
            aria-label="Choose color"
          />
        </PopoverTrigger>
        
        <PopoverContent className="w-64 p-3">
          <div className="mb-3">
            <input
              type="color"
              value={hexValue}
              onChange={handlePickerChange}
              className="w-full h-10 rounded-lg cursor-pointer"
            />
          </div>
          
          <div className="mb-3">
            <Input
              value={hexValue}
              onChange={handleHexChange}
              maxLength={7}
              className="font-mono"
              placeholder="#FFFFFF"
            />
          </div>
          
          <div className="grid grid-cols-4 gap-2">
            {colorPalette.map((color) => (
              <button
                key={color}
                type="button"
                className={cn(
                  "w-full h-8 rounded-md border",
                  color === hexValue
                    ? "border-primary-purple ring-2 ring-secondary-purple"
                    : "border-neutral hover:border-primary-purple"
                )}
                style={{ backgroundColor: color }}
                onClick={() => handlePaletteSelect(color)}
                aria-label={color}
              />
            ))}
          </div>
        </PopoverContent>
      </Popover>
    </div>
  );
};

/**
 * ColorPickerWithTransparency Component
 * 
 * Extends the ColorPicker with transparency control
 * 
 * @param {Object} props - Component props
 * @param {string} props.value - The current color value in hex format
 * @param {number} props.transparency - Transparency value 0-1
 * @param {Function} props.onChange - Callback when color changes
 * @param {Function} props.onTransparencyChange - Callback when transparency changes
 * @param {string} props.label - Label for the color picker
 * @param {string} props.className - Additional CSS classes
 * @returns {JSX.Element} ColorPickerWithTransparency component
 */
export const ColorPickerWithTransparency = ({
  value = '#FFFFFF',
  transparency = 0,
  onChange,
  onTransparencyChange,
  label,
  className = "",
  ...props
}) => {
  // Convert transparency percentage (0-100) to alpha (0-1)
  const percentToAlpha = (percent) => percent / 100;
  
  // Handle transparency slider change
  const handleTransparencyChange = (e) => {
    const newValue = parseFloat(e.target.value);
    onTransparencyChange(percentToAlpha(newValue));
  };
  
  return (
    <div className={cn("flex flex-col", className)} {...props}>
      <div className="flex items-center gap-3">
        <ColorPicker
          value={value}
          onChange={onChange}
          label={label}
        />
        
        <div className="flex-1">
          <input
            type="range"
            min="0"
            max="100"
            value={transparency * 100}
            onChange={handleTransparencyChange}
            className={cn(
              "w-full h-1.5 bg-bg-light rounded-full appearance-none cursor-pointer",
              "dark:bg-[#2E2E3E]",
              "[&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:w-4",
              "[&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-primary-purple [&::-webkit-slider-thumb]:dark:bg-accent-indigo"
            )}
          />
          <div className="flex justify-between mt-1">
            <span className="text-body-small text-neutral">0%</span>
            <span className="text-body-small text-neutral">100%</span>
          </div>
        </div>
      </div>
    </div>
  );
};
