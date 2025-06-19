import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Type } from 'lucide-react';
import { AwardsSettings } from './types';

interface TextTabProps {
  settings: AwardsSettings;
  updateSetting: (section: keyof AwardsSettings, key: string, value: any) => void;
  availableFonts?: string[];
}

export function TextTab({ settings, updateSetting, availableFonts = [] }: TextTabProps) {
  const fontOptions = [
    'AvenirNextLTProBold.otf',
    'DejaVuSans.ttf',
    'Arial',
    'Helvetica',
    'Times New Roman',
    'Courier New',
    ...availableFonts
  ].filter((font, index, arr) => arr.indexOf(font) === index); // Remove duplicates

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <Type className="h-5 w-5" />
          Text Settings
        </CardTitle>
        <CardDescription>
          Configure font, size, and text appearance for awards badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className="space-y-2">
            <Label htmlFor="font">Primary Font</Label>
            <Select
              value={settings.Text.font}
              onValueChange={(value) => updateSetting('Text', 'font', value)}
              disabled={!settings.General.enabled}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a font..." />
              </SelectTrigger>
              <SelectContent>
                {fontOptions.map((font) => (
                  <SelectItem key={font} value={font}>
                    {font}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="fallback-font">Fallback Font</Label>
            <Select
              value={settings.Text.fallback_font}
              onValueChange={(value) => updateSetting('Text', 'fallback_font', value)}
              disabled={!settings.General.enabled}
            >
              <SelectTrigger>
                <SelectValue placeholder="Select a font..." />
              </SelectTrigger>
              <SelectContent>
                {fontOptions.map((font) => (
                  <SelectItem key={font} value={font}>
                    {font}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="text-color">Text Color</Label>
            <div className="flex items-center space-x-2">
              <input
                type="color"
                value={settings.Text['text-color']}
                onChange={(e) => updateSetting('Text', 'text-color', e.target.value)}
                disabled={!settings.General.enabled}
                className="w-12 h-10 border rounded cursor-pointer disabled:opacity-50"
              />
              <Input
                type="text"
                value={settings.Text['text-color']}
                onChange={(e) => updateSetting('Text', 'text-color', e.target.value)}
                disabled={!settings.General.enabled}
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
              disabled={!settings.General.enabled}
              placeholder="90"
            />
            <div className="text-sm text-muted-foreground">
              Recommended: 90px for awards text visibility
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
