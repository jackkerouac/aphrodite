import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Circle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"

interface ColorPickerProps {
  color: string;
  onChange: (color: string) => void;
  label?: string;
  colors?: string[];
}

const ColorPicker: React.FC<ColorPickerProps> = ({
  color,
  onChange,
  label,
  colors = [
      '#ffffff', '#f5f5f5', '#dcdcdc', '#c0c0c0', '#a9a9a9', '#808080',
      '#000000', '#fa8072', '#ff6347', '#ff4500', '#ff0000', '#dc143c',
      '#b22222', '#8b0080', '#ffc300', '#ff851b', '#f08080', '#e67e22',
      '#d35400', '#ff8c00', '#ffa500', '#ff7f50', '#ffb6c1', '#ffdab9',
      '#ffe4e1', '#fff0f5', '#f0f8ff', '#e6e6fa', '#d8bfd8', '#c71585',
      '#ee82ee', '#da70d6', '#ff00ff', '#ff00ff', '#ba55d3', '#9932cc',
      '#800080', '#4b0082', '#6a5acd', '#483d8b', '#00008b', '#0000cd',
      '#0000ff', '#4169e1', '#6495ed', '#b0e0e6', '#afeeee', '#add8e6',
      '#87cefa', '#87ceeb', '#00bfff', '#5f9ea0', '#00ced1', '#40e0d0',
      '#48d1cc', '#00ffff', '#00ffff', '#7fffd4', '#66cdaa', '#2e8b57',
      '#228b22', '#006400', '#008000', '#228b22', '#2e8b57', '#3cb371',
      '#90ee90', '#98fb98', '#adff2f', '#7fff00', '#7cfc00', '#00ff00',
      '#32cd32', '#00ff7f', '#00fa9a', '#556b2f', '#6b8e23', '#808080',
      '#8fbc8f', '#a9a9a9', '#c0c0c0', '#d3d3d3', '#dcdcdc', '#f5f5f5',
      '#fffafa', '#ffffff'
  ]
}) => {
  const [inputValue, setInputValue] = useState(color);
  
  // Handle input change and validate hex color
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    setInputValue(newValue);
    
    // Only update the actual color if it's a valid hex color
    if (/^#[0-9A-F]{6}$/i.test(newValue)) {
      onChange(newValue);
    }
  };
  
  // Handle color selection from picker
  const handleColorSelect = (selectedColor: string) => {
    setInputValue(selectedColor);
    onChange(selectedColor);
  };

  return (
    <div className="flex items-center gap-2">
      <Popover>
        <PopoverTrigger asChild>
          <Button 
            variant="outline" 
            size="icon" 
            className="h-8 w-8 p-0"
            aria-label="Pick a color"
          >
            <div 
              className="h-6 w-6 rounded-full border border-gray-200"
              style={{ backgroundColor: color }}
            />
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-auto p-3" align="start">
          <div className="grid grid-cols-10 gap-1">
            {colors.map((colorOption) => (
              <div
                key={colorOption}
                className={cn(
                  "h-5 w-5 rounded-full cursor-pointer border hover:scale-110 transition-transform",
                  colorOption === color ? "border-primary border-2" : "border-gray-200"
                )}
                style={{ backgroundColor: colorOption }}
                onClick={() => handleColorSelect(colorOption)}
                title={colorOption}
              />
            ))}
          </div>
        </PopoverContent>
      </Popover>
      
      <Input
        value={inputValue}
        onChange={handleInputChange}
        onBlur={() => {
          // Revert to current color if invalid input on blur
          if (!/^#[0-9A-F]{6}$/i.test(inputValue)) {
            setInputValue(color);
          }
        }}
        className="w-24 h-8 font-mono text-xs"
        placeholder="#000000"
      />
    </div>
  );
};

export default ColorPicker;