import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { AudioSettings } from './types';

interface BorderTabProps {
  settings: AudioSettings;
  updateSetting: (path: string, value: any) => void;
}

export function BorderTab({ settings, updateSetting }: BorderTabProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Border Settings</CardTitle>
        <CardDescription>
          Configure badge border appearance for audio badges
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="space-y-2">
            <Label htmlFor="border-color">Border Color</Label>
            <div className="flex gap-2">
              <input
                type="color"
                value={settings.Border['border-color']}
                onChange={(e) => updateSetting('Border.border-color', e.target.value)}
                className="w-12 h-10 rounded border border-input"
              />
              <Input
                value={settings.Border['border-color']}
                onChange={(e) => updateSetting('Border.border-color', e.target.value)}
                placeholder="#000000"
                className="flex-1"
              />
            </div>
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="border-radius">Border Radius</Label>
            <Input
              id="border-radius"
              type="number"
              min="0"
              value={settings.Border['border-radius']}
              onChange={(e) => updateSetting('Border.border-radius', parseInt(e.target.value) || 10)}
            />
          </div>
          
          <div className="space-y-2">
            <Label htmlFor="border-width">Border Width</Label>
            <Input
              id="border-width"
              type="number"
              min="0"
              value={settings.Border.border_width}
              onChange={(e) => updateSetting('Border.border_width', parseInt(e.target.value) || 1)}
            />
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
