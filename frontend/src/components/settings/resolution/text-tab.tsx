import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Type } from 'lucide-react';
import { FontSelect } from '@/components/ui/font-select';
import { ResolutionSettings } from './types';

interface TextTabProps {
  settings: ResolutionSettings;
  updateSetting: (section: keyof ResolutionSettings, key: string, value: any) => void;
  availableFonts?: string[];
}

export function TextTab({ settings, updateSetting, availableFonts = [] }: TextTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Type className="h-5 w-5" />
          Text Settings
        </CardTitle>
        <CardDescription>
          Configure font, size, and text appearance for resolution badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="font">Primary Font</Label>
            <FontSelect
              value={settings.Text.font}
              onValueChange={(value) => updateSetting('Text', 'font', value)}
              availableFonts={availableFonts}
              placeholder="Select a font..."
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="fallback-font">Fallback Font</Label>
            <FontSelect
              value={settings.Text.fallback_font}
              onValueChange={(value) => updateSetting('Text', 'fallback_font', value)}
              availableFonts={availableFonts}
              placeholder="Select a font..."
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="text-color">Text Color</Label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={settings.Text['text-color']}
                onChange={(e) => updateSetting('Text', 'text-color', e.target.value)}
                className="w-12 h-10 border rounded cursor-pointer"
              />
              <Input
                type="text"
                value={settings.Text['text-color']}
                onChange={(e) => updateSetting('Text', 'text-color', e.target.value)}
                className="flex-1"
                placeholder="#FFFFFF"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="text-size">Text Size</Label>
            <Input
              id="text-size"
              type="number"
              min="10"
              value={settings.Text['text-size']}
              onChange={(e) => updateSetting('Text', 'text-size', parseInt(e.target.value) || 90)}
              placeholder="90"
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
