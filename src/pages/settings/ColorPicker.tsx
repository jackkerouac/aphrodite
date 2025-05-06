import React from 'react';
import { Button } from '@/components/ui/button';
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover';
import { Circle } from 'lucide-react';
import { cn } from '@/lib/utils';
import { Label } from "@/components/ui/label"

const ColorPicker = ({
    value,
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
}: {
    value: string,
    onChange: (color: string) => void,
    label: string,
    colors?: string[]
}) => {
    return (
        <div className="space-y-2">
            <Label htmlFor={label}>{label}</Label>
            <Popover>
                <PopoverTrigger asChild>
                    <Button
                        variant="outline"
                        className={cn(
                            "w-24 h-9 p-0 flex items-center justify-start gap-2",
                            value
                        )}
                    >
                        <Circle className="h-4 w-4" style={{ color: value }} />
                        <span>{value}</span>
                    </Button>
                </PopoverTrigger>
                <PopoverContent className="w-auto p-4" align="start">
                    <div className="grid grid-cols-6 gap-2">
                        {colors.map((color) => (
                            <div
                                key={color}
                                className="h-6 w-6 rounded-full cursor-pointer border border-gray-200 hover:border-gray-300"
                                style={{ backgroundColor: color }}
                                onClick={() => onChange(color)}
                                title={color}
                            />
                        ))}
                    </div>
                </PopoverContent>
            </Popover>
        </div>
    );
};

export default ColorPicker;