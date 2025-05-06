import React from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import ColorPicker from './ColorPicker';
import ShadowSettings from './ShadowSettings';

interface GeneralSettingsCardProps {
    settings: any; // Replace 'any' with a more specific type if available
    handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
    handleColorChange: (key: string, value: string) => void;
    handleToggleChange: (key: string, value: boolean) => void;
    handlePositionChange: (value: string) => void;
    handleResolutionChange: (value: string) => void;
    selectedResolution: string;
    onSubmit: (e: React.FormEvent) => Promise<void>;
    saving: boolean;
    isSaveDisabled: boolean;
    resolutionOptions: string[];
}

const GeneralSettingsCard: React.FC<GeneralSettingsCardProps> = ({
    settings,
    handleChange,
    handleColorChange,
    handleToggleChange,
    handlePositionChange,
    handleResolutionChange,
    selectedResolution,
    onSubmit,
    saving,
    isSaveDisabled,
    resolutionOptions,
}) => {
    return (
        <Card className="space-y-4">
            <CardHeader>
                <h2 className="text-xl font-semibold">General Settings</h2>
                <p className="text-sm text-muted-foreground">Manage the basic appearance of your badges.</p>
            </CardHeader>
            <CardContent className="space-y-4">
                <form onSubmit={onSubmit} className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="resolution_type">Resolution Type</Label>
                        <Select onValueChange={handleResolutionChange} value={selectedResolution}>
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Select resolution type" />
                            </SelectTrigger>
                            <SelectContent>
                                {resolutionOptions.map((option) => (
                                    <SelectItem key={option} value={option}>
                                        {option}
                                    </SelectItem>
                                ))}
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="margin">Margin/Padding</Label>
                        <Input
                            type="number"
                            id="margin"
                            name="margin"
                            value={settings.margin ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required
                        />
                        <p className="text-xs text-muted-foreground">
                            Distance from Poster Edge
                        </p>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="position">Position</Label>
                        <Select onValueChange={handlePositionChange} value={settings.position}>
                            <SelectTrigger className="w-full">
                                <SelectValue placeholder="Select position" />
                            </SelectTrigger>
                            <SelectContent>
                                <SelectItem value="top-left">Top Left</SelectItem>
                                <SelectItem value="top-right">Top Right</SelectItem>
                                <SelectItem value="bottom-left">Bottom Left</SelectItem>
                                <SelectItem value="bottom-right">Bottom Right</SelectItem>
                            </SelectContent>
                        </Select>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="size">Size (%)</Label>
                        <div className="flex items-center gap-2">
                            <Input
                                type="range"
                                id="size"
                                name="size"
                                min="50"
                                max="200"
                                step="5"
                                value={settings.size ?? 100}
                                onChange={handleChange}
                                className="flex-1"
                                required
                            />
                            <span className="text-sm w-12 text-right">{settings.size ?? 100}%</span>
                        </div>
                        <p className="text-xs text-muted-foreground">
                            Scale the badge size (50% to 200%)
                        </p>
                    </div>
                    <ColorPicker
                        label="Background Color"
                        value={settings.background_color}
                        onChange={(color) => handleColorChange('background_color', color)}
                    />
                    <div className="space-y-2">
                        <Label htmlFor="background_transparency">Background Transparency</Label>
                        <Input
                            type="number"
                            id="background_transparency"
                            name="background_transparency"
                            step="0.1"
                            min="0"
                            max="1"
                            value={settings.background_transparency ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="border_radius">Border Radius</Label>
                        <Input
                            type="number"
                            id="border_radius"
                            name="border_radius"
                            step="0.1"
                            value={settings.border_radius ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required
                        />
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="border_width">Border Width</Label>
                        <Input
                            type="number"
                            id="border_width"
                            name="border_width"
                            step="0.1"
                            value={settings.border_width ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required
                        />
                    </div>
                    <ColorPicker
                        label="Border Color"
                        value={settings.border_color}
                        onChange={(color) => handleColorChange('border_color', color)}
                    />
                    <div className="space-y-2">
                        <Label htmlFor="border_transparency">Border Transparency</Label>
                        <Input
                            type="number"
                            id="border_transparency"
                            name="border_transparency"
                            step="0.1"
                            min="0"
                            max="1"
                            value={settings.border_transparency ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required
                        />
                    </div>

                    <ShadowSettings
                        settings={settings}
                        handleColorChange={handleColorChange}
                        handleChange={handleChange}
                        handleToggleChange={handleToggleChange}
                    />

                    <div className="space-y-2">
                        <Label htmlFor="z_index">Z Index</Label>
                        <Input
                            type="number"
                            id="z_index"
                            name="z_index"
                            value={settings.z_index ?? ''}
                            onChange={handleChange}
                            className="w-32"
                            required
                        />
                    </div>
                    <div className="flex justify-end">
                        <Button
                            type="submit"
                            variant="default"
                            className="bg-black text-white"
                            disabled={isSaveDisabled || saving}
                        >
                            {saving ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
                            Save Changes
                        </Button>
                    </div>
                </form>
            </CardContent>
        </Card>
    );
};

export default GeneralSettingsCard;
