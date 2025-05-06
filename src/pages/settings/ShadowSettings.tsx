import React from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import ColorPicker from './ColorPicker'; // Import the ColorPicker component

const ShadowSettings = ({
    settings,
    handleColorChange,
    handleChange,
    handleToggleChange
}: {
    settings: any,
    handleColorChange: (key: string, value: string) => void,
    handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void,
    handleToggleChange: (key: string, value: boolean) => void
}) => {
    return (
        <div className="space-y-4 border-t pt-4 mt-4">
            <div className="flex items-center justify-between">
                <div>
                    <Label htmlFor="shadow_toggle" className="font-medium">Enable Shadow</Label>
                    <p className="text-xs text-muted-foreground">Add a drop shadow to the badge</p>
                </div>
                <Switch
                    id="shadow_toggle"
                    name="shadow_toggle"
                    checked={settings.shadow_toggle}
                    onCheckedChange={(checked) => handleToggleChange('shadow_toggle', checked)}
                />
            </div>

            {settings.shadow_toggle && (
                <div className="pl-4 border-l space-y-4">
                    <ColorPicker
                        label="Shadow Color"
                        value={settings.shadow_color}
                        onChange={(color) => handleColorChange('shadow_color', color)}
                        colors={[
                            '#000000', '#1a1a1a', '#333333', '#4d4d4d', '#666666', '#808080',
                            '#999999', '#b3b3b3', '#cccccc', '#e6e6e6'
                        ]}
                    />

                    <div className="space-y-2">
                        <Label htmlFor="shadow_blur_radius">Blur Radius</Label>
                        <Input
                            type="number"
                            id="shadow_blur_radius"
                            name="shadow_blur_radius"
                            step="0.1"
                            value={settings.shadow_blur_radius ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required={settings.shadow_toggle}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="shadow_offset_x">X Offset</Label>
                        <Input
                            type="number"
                            id="shadow_offset_x"
                            name="shadow_offset_x"
                            step="0.1"
                            value={settings.shadow_offset_x ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required={settings.shadow_toggle}
                        />
                    </div>

                    <div className="space-y-2">
                        <Label htmlFor="shadow_offset_y">Y Offset</Label>
                        <Input
                            type="number"
                            id="shadow_offset_y"
                            name="shadow_offset_y"
                            step="0.1"
                            value={settings.shadow_offset_y ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required={settings.shadow_toggle}
                        />
                    </div>
                </div>
            )}
        </div>
    );
};

export default ShadowSettings;